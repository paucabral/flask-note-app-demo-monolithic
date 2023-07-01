function check_pass() {
  let password = document.getElementById('floatingPassword').value;
  let password2 = document.getElementById('floatingPassword2').value;
  if (password == password2) {
    document.getElementById('signupBtn').disabled = false;
  }
  else {
    document.getElementById('signupBtn').disabled = true;
  }
}