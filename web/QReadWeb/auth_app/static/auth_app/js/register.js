$('#register-form').on('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the form data
    var formData = $(this).serialize();

    // Send the data to the server using AJAX
    $.ajax({
        type: 'POST',
        url: '/api/register/',
        data: formData,
        success: function(response) {
            // Handle success response
            if (response.success) {
                window.location.href = '/';
            } else {
                alert('Registration failed: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert('An error occurred: ' + error);
        }
    });
});