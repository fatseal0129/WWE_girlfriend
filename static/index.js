var input = document.getElementById('message');
var ask_text = document.getElementById('ask_text');
var response_text = document.getElementById('response_text')
var ask_text_prope = window.getComputedStyle(ask_text,'::before');
var b = Boolean(false);
var girl = document.getElementById('girl');
var response = document.getElementById('response_text')
let Value = "";

input.addEventListener("keypress", function(event){
	if (event.key == "Enter"){
		event.preventDefault();
		//document.getElementById("myBtn").click();

		//將inputbox暫時取消無法打字
		input.disabled = true;

		//將inputbox中的值存到Value變數中
		Value = input.value;
		//將回應句改成Value
		ask_text.innerHTML = Value;

		//ask_text_prope.animation = "typewriter 1s steps("+ Value.length +") forwards";
		console.log(Value.length)

		//顯示回應(原先為none)
		ask_text.style.display = "block";

		console.log({"res" : Value})
		
		$.when(ajax1()).done(function(a1){
			input.disabled = false;
		});
		
	}

})

function ajax1(){
	return $.ajax({
		url:"/qwer",
		method:"POST",
		data:{"res" : Value},
		success: (res)=>{
			console.log("the string you put is : " + res)
			response_text.innerHTML = res
		},
	  });
}

//https://stackoverflow.com/questions/51135498/flask-update-the-page-content-without-redirection-in-ajax-jquery

function trans(){
	if(b == false){
		//girl.src = "${window.static_folder}/m.png"
		girl.src = "/static/m.png"
		//girl.src="m.png"
		// response.style="color : colors.black";
		b = true;
	}
	else {
		//girl.src = "${window.static_folder}/g.png"
		girl.src = "/static/g.png"
		b = false
	}
}

