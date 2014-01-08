$(function() {  
  
    $('h4').click(function() {  
        $(this).slideUp().next('input').slideDown();  
    });  
  
    $('ul#photos input').change(function() {  
  
        var id = $(this).parent('li').find('img').attr('id');  
        var thisParam = $(this);  
        var title = $(this).val();  
  
        $.ajax({  
  
            type: 'POST',  
            url: 'changePhotoTitle.php',  
            data: 'title=' + title + '&id=' + id,  
  
            success: function(response) {  
                $('input').slideUp();  
                $(thisParam).prev('h4').text(title).slideDown();  
  
                $('#response').fadeIn(1000).empty().append(response).prepend('<span id="x">X</span>');  
  
                $('span#x').click(function() {  
                    $('div#response').fadeOut('slow');  
                });  
            }  
        });  
    });  
});  

$(function(){
    Test = {
        UpdatePreview: function(obj){
          // if IE < 10 doesn't support FileReader
          if(!window.FileReader){
             // don't know how to proceed to assign src to image tag
          } else {
             var reader = new FileReader();
             var target = null;

             reader.onload = function(e) {
              target =  e.target || e.srcElement;
              $("Img").attr("src", target.result);
             };
              reader.readAsDataURL(obj.files[0]);
          }
        }
    };
});
