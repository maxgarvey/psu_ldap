  $(document).ready( function(){
   $("#id_modify_group_name").attr("size", "50");
   $("#id_group_preferredcn").attr("size", "50");
   $("#id_group_room").attr("size", "50");
   $("#id_group_phone").attr("size", "50");
   $("#id_group_email").attr("size", "50");
   $("#id_group_name").attr("size", "50");
   $("#id_group_labeledUri").attr("size", "50");

   //this line hides the form initially
   $("#modify")       .addClass("inner").hide();

   //parse the json that got sent back inside of form div
   var results = JSON.parse(
    $("#success #form_div").html()
   );
   //console.log("results: " + results); //debug
   //console.log("results.hasOwnProperty('match'): " + 
   // results.hasOwnProperty("match")); //debug

   //the main obj we're interested in is in the match attribute
   if(results.hasOwnProperty("match")){
    //assume there's no labeledUri
    var has_labeledUri = false;
    //start the list we'll use for output
    var success_output = "<ul id='results_ul'>";

    //for each list element (matching entry)
    for(i=0;i<results.match.length;i++){

     //get all of the fields
     var my_dn              = results.match[i][0];
     var my_cn              = results.match[i][1].cn;
     var my_preferredcn     = results.match[i][1].preferredcn;
     var my_roomNumber      = results.match[i][1].roomNumber;
     var my_telephoneNumber = results.match[i][1].telephoneNumber;
     var my_mail            = results.match[i][1].mail;
     var my_labeledUri      = results.match[i][1].labeledUri;

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
     //set this boo if there is a labeledUri
     else{
      has_labeledUri = true;
     }

     //make a json string to add as data field to the "modify" 
     //button for this entry
     var my_data = JSON.stringify(
      {"dn":my_dn, "cn":my_cn, "preferredcn":my_preferredcn, "roomNumber":my_roomNumber,
      "telephoneNumber":my_telephoneNumber,"mail":my_mail,"labeledUri":my_labeledUri}
     );

     //add all the info to what will be displayed to the user.
     success_output += 
      "<div id='"+my_dn+"_div'><dl>"+

      "<strong><dt>Group DN:</dt></strong><dd>"              + my_dn           + "</dd>"+
      "<strong><dt>Group Name (cn):</dt></strong><dd>"       + my_cn           + "</dd>"+
      "<strong><dt>Preferredcn:</dt></strong><dd>"           + my_preferredcn  + "</dd>"+
      "<strong><dt>Room:</dt></strong><dd>"                  + my_roomNumber   + "</dd>"+
      "<strong><dt>Phone:</dt></strong><dd>"                 + my_telephoneNumber  + "</dd>"+
      "<strong><dt>Email:</dt></strong><dd>"                 + my_mail        + "</dd>";

     //optional field
     if(has_labeledUri){
      success_output +=
       "<strong><dt>Labeled URI:</dt></strong><dd>"          + my_labeledUri   + "</dd>";
     }

      //add button
      success_output += "</dl><button class='modify_this' data='"+my_data+"'>Modify</button></div><br/>";
    }

    //place it in the DOM
    success_output += "</ul>";
    $("#success #form_div").html(success_output);
   } //end if(results.hasOwnProperty("match"))

   //handle the error case
   else{
    var result_message = results.no_match;
    $("#success #form_div").html(result_message);
   }

   //change the form contents when the user clicks the button
   $(".modify_this") .click( function(){

    //console.log(this); //debug
    //console.log(this.getAttribute("data")); //debug

    var my_data = JSON.parse(this.getAttribute("data"));

    f = document.forms['modify_form'];

    f.elements['id_group_dn']          .value=my_data["dn"];
    f.elements['id_modify_group_name'] .value=my_data["cn"];
    f.elements['id_group_preferredcn'] .value=my_data["preferredcn"];
    f.elements['id_group_room']        .value=my_data["roomNumber"];
    f.elements['id_group_phone']       .value=my_data["telephoneNumber"];
    f.elements['id_group_email']       .value=my_data["mail"];
    f.elements['id_group_labeledUri']  .value=my_data["labeledUri"];

    $("#dn_display").html(my_data["dn"]);
    $("#dn_display").show();

    $("#group_dn_div").hide();
    $("#labeledUri_div").hide();
    $("#modify").show();
    $("#success").hide();

   });

  //this will hide the list and show the form when the user
  //picks one to modify.
  $("#modify_cancel").click( function(){
   $("#modify").hide();
   $("#success").show();
  });

});
