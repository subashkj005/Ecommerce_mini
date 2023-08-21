console.log('add to cart loading')

$(document).ready(function() {
    $('#add-to-cart-btn').click(function(e) {
      e.preventDefault();
      var variantId = $(this).data('variant-id');

      $.ajax({
        url: '/add_to_cart/' + variantId + '/',
        type: 'GET',
        success: function(response) {
          // Show custom success notification
          $('#cart-notification').text('Item added to Cart').fadeIn().delay(2000).fadeOut();

          // Refresh the page after success
          location.reload();
        },
        error: function(xhr, status, error) {
          alert('Error occurred while adding item to cart.');
          console.log(xhr.responseText);
        }
      });
    });
  });