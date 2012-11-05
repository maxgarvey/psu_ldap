  $(document).ready( function(){

   var get_recent = function() {
    $.ajax({
      url:"/recent/",
      type:"GET",
      data:"",
      success: function(a) {
        $("#waiting") .hide();
        $("#recent")  .html("<div id='form_div'>"+a+"</div>");
        $("#recent")  .show();
      }
    });
      $("#recent")  .hide();
      $("#waiting") .show();
   }

   get_recent();

   $("#recent_view")  .click( function(){
    get_recent();
   });

});
