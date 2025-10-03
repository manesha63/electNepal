/**
 * ElectNepal Candidate Dashboard Scripts
 * Handles all dashboard-related functionality without inline scripts for CSP compliance
 */

// Modal management functions
function openEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.remove('hidden');
        // Focus first input in modal
        setTimeout(() => {
            const firstInput = modal.querySelector('textarea, input');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Event deletion function
function deleteEvent(eventId) {
    const confirmMsg = document.documentElement.lang === 'ne'
        ? 'के तपाईं यो कार्यक्रम मेटाउन निश्चित हुनुहुन्छ?'
        : 'Are you sure you want to delete this event?';

    if (confirm(confirmMsg)) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        fetch(`/candidates/events/${eventId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                const errorMsg = document.documentElement.lang === 'ne'
                    ? 'कार्यक्रम मेटाउन सकिएन'
                    : 'Failed to delete event';
                alert(errorMsg);
            }
        }).catch(error => {
            console.error('Error deleting event:', error);
            const errorMsg = document.documentElement.lang === 'ne'
                ? 'कार्यक्रम मेटाउन सकिएन'
                : 'Failed to delete event';
            alert(errorMsg);
        });
    }
}

// Post deletion function (if needed)
function deletePost(postId) {
    const confirmMsg = document.documentElement.lang === 'ne'
        ? 'के तपाईं यो पोस्ट मेटाउन निश्चित हुनुहुन्छ?'
        : 'Are you sure you want to delete this post?';

    if (confirm(confirmMsg)) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        fetch(`/candidates/posts/${postId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                const errorMsg = document.documentElement.lang === 'ne'
                    ? 'पोस्ट मेटाउन सकिएन'
                    : 'Failed to delete post';
                alert(errorMsg);
            }
        }).catch(error => {
            console.error('Error deleting post:', error);
            const errorMsg = document.documentElement.lang === 'ne'
                ? 'पोस्ट मेटाउन सकिएन'
                : 'Failed to delete post';
            alert(errorMsg);
        });
    }
}

// Initialize dashboard event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Edit profile button
    const editProfileBtn = document.querySelector('[data-action="edit-profile"]');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', openEditModal);
    }

    // Close modal buttons
    const closeModalBtns = document.querySelectorAll('[data-close-modal="edit"]');
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', closeEditModal);
    });

    // Close modal when clicking outside
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('click', function(event) {
            if (event.target === editModal) {
                closeEditModal();
            }
        });
    }

    // Delete event buttons
    const deleteEventBtns = document.querySelectorAll('[data-delete-event]');
    deleteEventBtns.forEach(btn => {
        const eventId = btn.getAttribute('data-delete-event');
        btn.addEventListener('click', () => deleteEvent(eventId));
    });

    // Delete post buttons
    const deletePostBtns = document.querySelectorAll('[data-delete-post]');
    deletePostBtns.forEach(btn => {
        const postId = btn.getAttribute('data-delete-post');
        btn.addEventListener('click', () => deletePost(postId));
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            if (editModal && !editModal.classList.contains('hidden')) {
                closeEditModal();
            }
        }
    });
});

// Export functions for use in templates
if (typeof window !== 'undefined') {
    window.openEditModal = openEditModal;
    window.closeEditModal = closeEditModal;
    window.deleteEvent = deleteEvent;
    window.deletePost = deletePost;
}
