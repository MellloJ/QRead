$('#register-form').on('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the form data
    var formData = $(this).serialize();

    // Send the data to the server using AJAX
    $.ajax({
        type: 'POST',
        url: '/login/api/register/', // Replace with your actual registration endpoint
        data: formData,
        success: function(response) {
            // Handle success response
            if (response.success) {
                Swal.fire({
                    text: "Usuário cadastrado com sucesso!",
                    icon: "success",
                    timer: 2000, // Alerta visível por 2 segundos (2000 ms)
                    timerProgressBar: true, // Exibe uma barra de progresso (opcional)
                    showConfirmButton: true // Oculta o botão "OK"
                }).then(function() {
                    // Redireciona após o alerta fechar
                    window.location.href = '/';
                });
            } else {
                Swal.fire({
                    text: "Erro ao cadastrar usuário!",
                    icon: "error", // Corrigido de "danger" para "error" (padrão do SweetAlert2)
                });
                console.error('Registration error:', response.error);
            }
        },
        error: function(xhr, status, error) {
            Swal.fire({
                text: "Erro ao cadastrar usuário!",
                icon: "error",
            });
            console.error('AJAX error:', status, error);
        }
    });
});