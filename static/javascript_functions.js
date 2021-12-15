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
