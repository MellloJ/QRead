$('#login-form').on('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the form data
    var formData = $(this).serialize();

    // Send the data to the server using AJAX
    $.ajax({
        type: 'POST',
        url: '/web/login/',
        data: formData,
        success: function(response) {
            // Handle success response
            if (response.status == 'success') {
                Swal.fire({
                    text: "Login realizado com sucesso!",
                    icon: "success",
                    timer: 2000, // Alert visible for 2 seconds (2000 ms)
                    timerProgressBar: true, // Shows a progress bar (optional)
                    showConfirmButton: true // Hides the "OK" button
                }).then(function() {
                    // Redirect after the alert closes
                    window.location.href = '/dashboard/';
                });
            } else {
                Swal.fire({
                    text: "Usuário ou senha incorretos!",
                    icon: "error", // Corrected from "danger" to "error" (SweetAlert2 standard)
                });
                console.error('Login error:', response.error);
            }
        },
        error: function(xhr, status, error) {
            Swal.fire({
                text: "Erro ao realizar login!",
                icon: "error",
            });
            console.error('AJAX error:', status, error);
        }
    });
});