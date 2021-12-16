/*
* Methods to hide and display tables when tab is clicked. Need to have a way no
* have the same method used in the same page qouting different diccionaries,
* taking the dic as a param is not feasible so the next best thing is duplicating
* the method however many times is needed on the same page. Apologies for the
* WET code.
*/
function displayTournaments1(new_active_keyword, containerType) {
  for (const prev_active_keyword of Object.keys(tabs_dic1)) {
    document.getElementById(tabs_dic1[prev_active_keyword]).classList.remove('active');
    document.getElementById(tables_dic1[prev_active_keyword]).style.display = "none";
  }

  document.getElementById(tabs_dic1[new_active_keyword]).classList.add('active');
  document.getElementById(tables_dic1[new_active_keyword]).style.display = containerType;
}

function displayTournaments2(new_active_keyword, containerType) {
  for (const prev_active_keyword of Object.keys(tabs_dic2)) {
    document.getElementById(tabs_dic2[prev_active_keyword]).classList.remove('active');
    document.getElementById(tables_dic2[prev_active_keyword]).style.display = "none";
  }

  document.getElementById(tabs_dic2[new_active_keyword]).classList.add('active');
  document.getElementById(tables_dic2[new_active_keyword]).style.display = containerType;
}

var msgDic = {
  "kick": "Are you sure you want to kick this user from the club?",
  "ban": "Are you sure you want to ban this user from the club?",
  "transfer_ownership": "Are you sure you want to give up ownership?",
  "withdraw_application": "Are you sure you want to withdraw your application?",
  "leave_club": "Are you sure you want to leave this club?",
  "accept_application": "Are you sure you want to accept this applicant?",
  "reject_application": "Are you sure you want to reject this applicant?",
  "delete_applications":'Are you sure you want to delete this club?',
  "withdraw_from_tournament": "Are you sure you want to leave this tournament?"
}
/*
* Method to pop up a message from diccionary to confirm action by user.
*/
function confirmMsg(msgType){

  if(confirm(msgDic[msgType])){
    return true;
  }else{
    event.stopPropagation(); event.preventDefault();
  }
}
