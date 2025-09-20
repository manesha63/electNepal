"""
Bilingual Validation System
Ensures all models and templates follow bilingual requirements
"""

import ast
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models


class BilingualValidator:
    """
    Validates that models and templates follow bilingual standards
    """

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_model(self, model):
        """
        Validate that a model follows bilingual standards
        """
        model_name = model.__name__

        # Get all text fields
        text_fields = []
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                field_name = field.name

                # Skip system fields
                if field_name in ['id', 'password', 'username', 'email', 'code']:
                    continue

                # Check if it's a base field without language suffix
                if not field_name.endswith('_en') and not field_name.endswith('_ne'):
                    text_fields.append(field_name)

        # Check each text field has bilingual versions
        for field_name in text_fields:
            en_field = f"{field_name}_en"
            ne_field = f"{field_name}_ne"

            has_en = hasattr(model, en_field)
            has_ne = hasattr(model, ne_field)

            if not has_en and not has_ne:
                self.warnings.append(
                    f"{model_name}.{field_name}: Consider making this field bilingual"
                )

    def validate_all_models(self):
        """
        Validate all models in the project
        """
        for model in apps.get_models():
            # Skip Django internal models
            if model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
                continue

            self.validate_model(model)

    def validate_template(self, template_path):
        """
        Check if template uses bilingual template tags
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for hardcoded text that should be translated
        issues = []

        # Common patterns that indicate untranslated text
        patterns = [
            ('Office:', 'Use {% trans "Office:" %}'),
            ('Seat:', 'Use {% trans "Seat:" %}'),
            ('From:', 'Use {% trans "From:" %}'),
            ('Email:', 'Use {% trans "Email:" %}'),
            ('Phone:', 'Use {% trans "Phone:" %}'),
            ('Contact', 'Use {% trans "Contact" %}'),
        ]

        for pattern, suggestion in patterns:
            if pattern in content and f'trans "{pattern}"' not in content:
                issues.append(f"{template_path}: Found '{pattern}' - {suggestion}")

        return issues

    def validate_all_templates(self, base_path):
        """
        Validate all templates in the project
        """
        template_issues = []

        for root, dirs, files in os.walk(base_path):
            # Skip migrations and venv
            if 'migrations' in root or '.venv' in root:
                continue

            for file in files:
                if file.endswith('.html'):
                    template_path = os.path.join(root, file)
                    issues = self.validate_template(template_path)
                    template_issues.extend(issues)

        return template_issues

    def generate_report(self):
        """
        Generate validation report
        """
        report = []
        report.append("=" * 60)
        report.append("BILINGUAL VALIDATION REPORT")
        report.append("=" * 60)

        if self.errors:
            report.append("\n❌ ERRORS (Must Fix):")
            for error in self.errors:
                report.append(f"  - {error}")
        else:
            report.append("\n✅ No critical errors found")

        if self.warnings:
            report.append("\n⚠️  WARNINGS (Should Consider):")
            for warning in self.warnings:
                report.append(f"  - {warning}")
        else:
            report.append("\n✅ No warnings")

        report.append("\n" + "=" * 60)
        return "\n".join(report)


class DevelopmentChecker:
    """
    Checks new development for bilingual compliance
    """

    @staticmethod
    def check_model_fields(model_code):
        """
        Check if new model code follows bilingual pattern
        """
        issues = []

        # Parse the Python code
        try:
            tree = ast.parse(model_code)
        except SyntaxError:
            return ["Code has syntax errors"]

        # Find CharField and TextField definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr'):
                    field_type = node.func.attr

                    if field_type in ['CharField', 'TextField']:
                        # Check if it's using bilingual pattern
                        parent = node
                        # This is simplified - in practice would need more complex AST analysis
                        issues.append(
                            f"Consider using BilingualCharField or BilingualTextField "
                            f"instead of {field_type}"
                        )

        return issues

    @staticmethod
    def generate_bilingual_model_template(model_name, fields):
        """
        Generate a template for a bilingual model
        """
        template = f"""
from django.db import models
from core.models_base import BilingualModel, BilingualCharField, BilingualTextField

class {model_name}(BilingualModel):
    '''
    {model_name} with automatic bilingual support
    '''

    # Define bilingual fields
    BILINGUAL_FIELDS = {fields}

"""

        for field in fields:
            template += f"    {field} = BilingualCharField(max_length=200)\n"

        template += """
    def __str__(self):
        return self.get_field_in_language('name')
"""

        return template


def run_validation():
    """
    Run full validation check
    """
    validator = BilingualValidator()

    # Validate models
    print("Checking models...")
    validator.validate_all_models()

    # Validate templates
    print("Checking templates...")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_issues = validator.validate_all_templates(base_path)
    validator.warnings.extend(template_issues)

    # Generate report
    report = validator.generate_report()
    print(report)

    return len(validator.errors) == 0