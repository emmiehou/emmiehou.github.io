document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    const formStatus = document.getElementById('formStatus');
    const emailError = document.getElementById('emailError');

    function validateEmail(email) {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    }

    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
        element.closest('.form-group').style.borderColor = '#ff4444';
    }

    function clearErrors() {
        emailError.style.display = 'none';
        formStatus.style.display = 'none';
        // Reset border colors
        form.querySelectorAll('.form-group input, .form-group textarea').forEach(input => {
            input.style.borderColor = '#333';
        });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        clearErrors();

        const email = form.email.value.trim();
        let isValid = true;

        // Validate email
        if (!validateEmail(email)) {
            showError(emailError, 'please enter a valid email address');
            form.email.style.borderColor = '#ff4444';
            isValid = false;
        }

        if (isValid) {
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'sending...';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                formStatus.textContent = 'thanks for your message! i\'ll get back to you soon.';
                formStatus.className = 'form-status success';
                formStatus.style.display = 'block';
                form.reset();
            })
            .catch(error => {
                formStatus.textContent = 'oops! something went wrong. please try again.';
                formStatus.className = 'form-status error';
                formStatus.style.display = 'block';
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = 'send message';
            });
        }
    });
});