$(document).ready( function(){

   //this function resets a form
   function resetForm(_form){
    _form.find('input:text, input:password, input:file, select').val('');
    _form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
   }

   //this block hides the forms initially
   $("#query").addClass("inner").hide();
   $("#instructions_div").addClass("inner").hide();
   $("#modify").addClass("inner").hide();
   $("#success").addClass("inner").hide();
   $("#waiting").addClass("inner").hide();

   //for each button, the other forms will slide up
   //and the relevant one will be displayed
   $("#query_view").click( function(){
    $("#instructions_div").slideUp();
    $("#modify").slideUp();
    $("#success").hide();
    $("#waiting").hide();
    $("#query").slideDown();

    //this line resets the form when the user clicks 
    //on the button for the other form
    resetForm($("#modify_form"));
   });

   $("#instructions_view").click( function(){
    $("#query").slideUp();
    $("#modify").slideUp();
    $("#success").hide();
    $("#waiting").hide()
    $("#instructions_div").slideDown();
   });

   $("#modify_view").click( function(){
    $("#query").slideUp();
    $("#instructions_div").slideUp();
    $("#success").hide();
    $("#waiting").hide()
    $("#modify").slideDown();

    //this line resets the form when the user clicks 
    //on the button for the other form
    //resetForm($("#query_form"));
   });
   //this block spoofs a form submit for the query form
   $("#query_submit").click( function() {
    $.ajax({
      url:"/query/",
      type:"POST",
      data:"csrfmiddlewaretoken="+$("input[type=hidden][name=csrfmiddlewaretoken]").attr("value")+
        "&group_name="+$("input[name=group_name]").val().replace('&','%26'),
      success:function(a){
         $('#waiting').slideUp();
         $('#success').html('<div id="form_div">'+a+' </div>');
         $('#success').slideDown();
         a_split = a.split('<br/>');
         $("#last_query").remove();
         //$("#modify_form").html('<span id="last_query">'+a_split[1]+'<br/></span>'+$("#modify_form").html());

         f = document.forms['modify_form'];

         f.elements['id_group_dn'].value=a_split[1].substring(4);

         c = (a_split[2].indexOf("['")+2);
         d =  a_split[2].indexOf("']");

         f.elements['id_group_name'].value=a_split[2].substring(c,d);

         c = (a_split[3].indexOf("['")+2);
         d =  a_split[3].indexOf("']");

         f.elements['id_group_preferredcn'].value=a_split[3].substring(c,d);

         c = (a_split[4].indexOf("['")+2);
         d =  a_split[4].indexOf("']");

         f.elements['id_group_room'].value=a_split[4].substring(c,d);

         c = (a_split[5].indexOf("['")+2);
         d =  a_split[5].indexOf("']");

         f.elements['id_group_phone'].value=a_split[5].substring(c,d);

         c = (a_split[6].indexOf("['")+2);
         d =  a_split[6].indexOf("']");

         f.elements['id_group_email'].value=a_split[6].substring(c,d);

         if (a_split.length > 7){
          c=(a_split[7].indexOf("['")+2);d=a_split[7].indexOf("']");
          f.elements['id_group_labeledUri'].value=a_split[7].substring(c,d);
         }
         else {
          f.elements['id_group_labeledUri'].value="NOT PERMITTED";
          $("#labeledUri_div").hide();
         }
        }
      }
    );
     $("#instructions_div").slideUp();
     $("#modify").slideUp();
     $("#query").slideUp();
     $("#waiting").slideDown();
    });
   //this block spoofs a form submit for the group form
   $("#modify_submit").click( function() {
    $.ajax({
     url:"/modify/",
     type:"POST",
     data:"csrfmiddlewaretoken=" + $("input[type=hidden][name=csrfmiddlewaretoken]").attr("value")+

      "&group_name="             + $("input[name=group_name]")       .val().replace('&','%26')+
      "&group_preferredcn="      + $("input[name=group_preferredcn]").val().replace('&','%26')+
      "&group_room="             + $("input[name=group_room]")       .val().replace('&','%26')+
      "&group_phone="            + $("input[name=group_phone]")      .val().replace('&','%26')+
      "&group_email="            + $("input[name=group_email]")      .val().replace('&','%26')+
      "labeledUri="              + $("input[name=group_labeledUri]") .val().replace('&','%26'),

      success:function(a){
       $('#waiting').slideUp();
       $('#success').html('<div id="form_div">'+a+' </div>');
       $('#success').slideDown();
      }
    });
    $("#instructions_div").slideUp();
    $("#modify").slideUp();
    $("#query").slideUp();
    $("#waiting").slideDown();
   });
});
