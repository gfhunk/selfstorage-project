//Fix BUG-06: Закрытие бургера
document.addEventListener('DOMContentLoaded', () => {
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav');
    if (burger && nav) {
        burger.addEventListener('click', () => nav.classList.toggle('nav--active'));
    }

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            let hasError = false;

            const requiredFields = form.querySelectorAll('input[required], select[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.border = '2px solid #DC3545';
                    hasError = true;
                } else {
                    field.style.border = 'none';
                }
            });

            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (field.value && !emailRegex.test(field.value)) {
                    field.style.border = '2px solid #DC3545';
                    hasError = true;
                }
            });

            const telFields = form.querySelectorAll('input[type="tel"]');
            telFields.forEach(field => {
                const digits = field.value.replace(/\D/g, '');
                if (field.value && digits.length < 10) {
                    field.style.border = '2px solid #DC3545';
                    hasError = true;
                }
            });

            if (hasError) {
                e.preventDefault();
                alert('Пожалуйста, проверьте правильность заполнения полей.');
            }
        });
    });
});