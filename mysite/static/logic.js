  $(document).ready( function(){

   //this function resets a form
   //function resetForm(_form){
   // _form.find('input:text, input:password, input:file, select').val('');
   // _form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
   //}

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
      //$("#success") .hide();
      $("#recent")  .hide();
      //$("#query")   .hide();
      //$("#modify")  .hide();
      $("#waiting") .show();
   }

   //this block hides the forms initially
   //$("#query")        .addClass("inner").hide();
   //$("#modify")       .addClass("inner").hide();
   //$("#success")      .addClass("inner").hide();
   //$("#waiting")      .addClass("inner").hide();
   //$("#l_nav_modify") .hide();
   get_recent();

   //for each button, the other forms will vanish
   //and the relevant one will be displayed
   //$("#query_view").click( function(){
   /*$("#l_nav_query").click( function(){

    $("#modify")  .hide();
    $("#recent")  .hide();
    $("#success") .hide();
    $("#waiting") .hide();
    $("#query")   .show();

    //this line resets the form when the user clicks 
    //on the button for the other form
    resetForm($("#modify_form"));
   });*/

   $("#recent_view")  .click( function(){
    //$("#query")       .hide();
    //$("#modify")      .hide();
    //$("#success")     .hide();
    //$("#waiting")     .hide()
    get_recent();
   });

   //$("#modify_view").click( function(){
   /*var update_modify = function() { 

    $(".modify_this") .click( function(){

     //console.log(this); //debug
     //console.log(this.getAttribute("data"));

     my_data = eval(this.getAttribute("data"));

     $("#query")       .hide();
     $("#recent")      .hide();
     //$("#success")     .hide();
     $("#waiting")     .hide();

    f = document.forms['modify_form'];

    $("#dn_display").html(my_data[0]);
         for (key in my_data[1]) {
          //console.log('in for loop'); //debug
          has_labeledUri = false;
          value = my_data[1][key];
          if (key == "cn"){
           f.elements['id_modify_group_name'].value = value;
          }
          else if (key == "preferredcn") {
           f.elements['id_group_preferredcn'].value = value;
          }
          else if (key == 'roomNumber') {
           f.elements['id_group_room'].value = value;
          }
          else if (key == 'telephoneNumber') {
           f.elements['id_group_phone'].value = value;
          }
          else if (key == 'mail') {
           f.elements['id_group_email'].value = value;
          }
          else if (key == 'labeledUri') {
           f.elements['id_group_labeledUri'].value = value;
           has_labeledUri = true;
          }
         }
         if (!has_labeledUri) {
          f.elements['id_group_labeledUri'].value = "NOT PERMITTED";
          $("#labeledUri_div").hide();
         }
         else {
          $("#labeledUri_div").show();
         }

    $("#modify")      .show();
    $("#success")     .hide();

    //this line resets the form when the user clicks 
    //on the button for the other form
    //resetForm($("#query_form"));
   });
   }

    //this function generates the results list after a query
    var make_results = function(a) {
     result_list = a['match'];
     result = "";
     for (o_i=0;o_i<result_list.length;o_i++) {
      just_the_cn = result_list[o_i][0].split(",")[0].split("=")[1]; 
      result += "<div id="+just_the_cn+"_div>";
      result += "<dl id="+just_the_cn+"_dl><dt>Group DN:</dt><dd>";
      result += result_list[o_i][0];
      result += "</dd>";
      for (o_key in result_list[o_i][1]) {
       if (o_key == "telephoneNumber" || o_key == "cn" || o_key == "preferredcn" || o_key == "mail" || o_key == "roomNumber" || o_key == "roomNumber" || o_key == "labeledUri")  {
        result += "<dt>";
        result += o_key;
        result += ":</dt>";
        for (i_i=0;i_i<result_list[o_i][1][o_key].length;i_i++) {
         result += "<dd>";
         result += result_list[o_i][1][o_key][i_i];
         result += "</dd>";
        }
       }
      }
      result += "</dl><button id=\"modify_"+just_the_cn+"_button\" class=\"modify_this\" data='"+JSON.stringify(a["match"][o_i])+"'>Modify</button></div><br/>";
     }
     return result;
    }

   /*var query_submit = function(query_event) {
    if(query_event) {
      query_event.preventDefault();
    }
    $.ajax({
      url:"/query/",
      type:"POST",
      data:"csrfmiddlewaretoken="+$("input[type=hidden][name=csrfmiddlewaretoken]").attr("value")+
        "&query_group_name="+$("input[name=query_group_name]").val().replace('&','%26'),
      dataType:"json",
      success:function(a){
         //console.log(a['success']); //debug
         if (a['success'] == 'true') {
          //console.log(a['match']);
          //console.log(a['match'].length);
          $("#l_nav_modify").html("Modify<ul id='modify_sublist'></ul>");
          //for (i=0; i<a['match'].length; i++) {
          // console.log(a['match'][i][0]);
          // list_items = $("#modify_sublist").html();
          // list_items += "<li id='"+a['match'][i][0].split(',')[0].split('=')[1]+"' class='modify_this' data='"+JSON.stringify(a['match'][i])+"'>"+a['match'][i][0]+"</li>";
          // $("#modify_sublist").html(list_items);
          //}
          formatted_results = make_results(a);
          $('#success')  .html('<div id="form_div">'+formatted_results+' </div>');
         }
         else {
          $('#success')  .html('<div id="form_div">'+JSON.stringify(a['no_match'])+' </div>');
         }

         $('#waiting')  .hide();
         $('#success')  .show();

         update_modify();

         //$("#l_nav_modify").show();
       }
      });
     $("#modify")   .hide();
     $("#query")    .hide();
     $("#waiting")  .show();

    }

   //this block spoofs a form submit for the query form
   $("#query_submit").click( function() {
    query_submit();
   });

   $("#query_form").submit( function(query_event) {
    query_submit(query_event);
   });  */

   /*var modify_submit = function(modify_event) {
    //modify_event.preventDefault();
    $.ajax({
     url:  "/modify/",
     type: "POST",
     data: "csrfmiddlewaretoken=" + $("input[type=hidden][name=csrfmiddlewaretoken]").attr("value")+

      "&group_dn="               + $("#dn_display")                   .html() .replace('&amp;','&') .replace('&','%26')+
      "&modify_group_name="      + $("input[name=modify_group_name]") .val()  .replace('&','%26')+
      "&group_preferredcn="      + $("input[name=group_preferredcn]") .val()  .replace('&','%26')+
      "&group_room="             + $("input[name=group_room]")        .val()  .replace('&','%26')+
      "&group_phone="            + $("input[name=group_phone]")       .val()  .replace('&','%26')+
      "&group_email="            + $("input[name=group_email]")       .val()  .replace('&','%26')+
      "&group_labeledUri="       + $("input[name=group_labeledUri]")  .val()  .replace('&','%26'),

      success:function(a){
       $('#waiting') .hide();
       $('#success') .html('<div id="form_div">'+a+' </div>');
       $('#success') .show();
      }
    });

      //this part is all a debug
      data_string = "csrfmiddlewaretoken=" + $("input[type=hidden][name=csrfmiddlewaretoken]").attr("value")+
      "&group_dn="               + $("#dn_display")                   .html() .replace('&amp;','&') .replace('&','%26') +
      "&modify_group_name="      + $("input[name=modify_group_name]") .val()  .replace('&','%26')+
      "&group_preferredcn="      + $("input[name=group_preferredcn]") .val()  .replace('&','%26')+
      "&group_room="             + $("input[name=group_room]")        .val()  .replace('&','%26')+
      "&group_phone="            + $("input[name=group_phone]")       .val()  .replace('&','%26')+
      "&group_email="            + $("input[name=group_email]")       .val()  .replace('&','%26')+
      "&group_labeledUri="       + $("input[name=group_labeledUri]")  .val()  .replace('&','%26');
      //console.log(data_string);


    $("#modify")   .hide();
    $("#query")    .hide();
    $("#waiting")  .show();
   }

   //this block spoofs a form submit for the group form
   $("#modify_submit").click( function() {
    modify_submit();
   });

   $("#modify_cancel").click( function(){
    $("#modify").hide();
    $("#success").show();
   });

   //this isn't working... don't know why
   $("#modify_form").submit( function(modify_event) {
    modify_submit(modify_event);
   });

   //want to bind enter key to modify_submit on focusin
   $("#modify_form").keypress( function(key_event) {
     if(key_event.keyCode == 13) {
      modify_submit();
     }
   });*/

});
