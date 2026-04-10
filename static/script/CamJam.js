
function toggleStatus(record) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        
    }
  };
  id = record.getAttribute('id')
  xhttp.open("GET", "toggle?id="+id, true);
  xhttp.send();
}