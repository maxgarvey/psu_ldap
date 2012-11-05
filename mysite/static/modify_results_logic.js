  $(document).ready( function(){
   //this block hides the forms initially

   var results = JSON.parse( $("#success #form_div").html() );
   //console.log(results);
   //console.log("results.hasOwnProperty('success'): " + 
   // results.hasOwnProperty("success"));

   if(results.hasOwnProperty("success")){
    //console.log("(results['success'] == true): " + (results['success'] == true));
    if(results['success'] == true){
     var output = "<dl id='results_dl'>";
     var has_labeledUri = false;

     var my_dn              = results['dn'];
     var my_cn              = results['cn'];
     var my_preferredcn     = results['preferredcn'];
     var my_roomNumber      = results['room'];
     var my_telephoneNumber = results['phone'];
     var my_mail            = results['email'];
     var my_labeledUri      = results['labeledUri'];
     //correct for possible missing items

     if(my_roomNumber      == undefined){
      my_roomNumber = "";
     }
     if(my_telephoneNumber == undefined){
      my_telephoneNumber = "";
     }
     if(my_mail            == undefined){
      my_mail = "";
     }
     if(my_labeledUri      == undefined){
      my_labeledUri = "";
     }
     else{
      has_labeledUri = true;
     }

     output += 
      "<strong>Modify Results:</strong><br/><dl>"+

      "<strong><dt>Group DN:</dt></strong><dd>"              + my_dn           + "</dd>"+
      "<strong><dt>Group Name (cn):</dt></strong><dd>"       + my_cn           + "</dd>"+
      "<strong><dt>Preferredcn:</dt></strong><dd>"           + my_preferredcn  + "</dd>"+
      "<strong><dt>Room:</dt></strong><dd>"                  + my_roomNumber   + "</dd>"+
      "<strong><dt>Phone:</dt></strong><dd>"                 + my_telephoneNumber  + "</dd>"+
      "<strong><dt>Email:</dt></strong><dd>"                 + my_mail        + "</dd>";

     if(has_labeledUri){
      output +=
       "<strong><dt>Labeled URI:</dt></strong><dd>"          + my_labeledUri   + "</dd>";
     }

      output += "</dl>";
    }
    else{
     var result_message = results['message'];
     $("#success #form_div").html(result_message);
    }
    $("#success #form_div").html(output);
   } //end if(results.hasOwnProperty("success"))

  else{
   $("#success #form_div").html("Improperly formatted response received:<br/><br/>"+JSON.stringify(results));
  }

});
