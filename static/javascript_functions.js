/*
* Method to hide and display tables when tab is clicked.
*/
function displayTournaments(new_active_keyword) {
  for (const prev_active_keyword of Object.keys(tabs_dic)) {
    document.getElementById(tabs_dic[prev_active_keyword]).classList.remove('active');
    document.getElementById(tables_dic[prev_active_keyword]).style.display = "none";
  }

  document.getElementById(tabs_dic[new_active_keyword]).classList.add('active');
  document.getElementById(tables_dic[new_active_keyword]).style.display = "table";
}
<<<<<<< HEAD

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
=======
>>>>>>> 1dee8cbc1b92e054599e6a13f7c6e6d4a69e279d
