

function init(){
  console.log("Detail enaced")
  if (test){
    $("#navbar").css("background-color", "#FFCECE");
    $("#profiles-href").attr("href","/adminpage/test-profile")
    $("#permette-href").attr("href","/adminpage/test-permittee")
  }
  else{
    $("#navbar").css("background-color", "#EAEFF4");
    $("#profiles-href").attr("href","/adminpage/profile")
    $("#permette-href").attr("href","/adminpage/permittee")
  }
}