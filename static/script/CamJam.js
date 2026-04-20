var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {

  }
};

function toggleStatus(record) {
//  alert("Toggle");
  id = record.getAttribute('id')
  xhttp.open("GET", "toggle?id="+id, true);
  xhttp.send();
}

function crap(){
  alert("Button pressed");
}

function release(record) {
//  alert("Release");
  
  id = record.getAttribute('id')
  xhttp.open("GET", "release?id="+id, true);
  xhttp.send();
  const element = document.getElementById(id);
  element.remove();
}
