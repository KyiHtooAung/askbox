document.write('<scr'+'ipt type="text/javascript" src="vue/dist/vue.js" ></scr'+'ipt>');
document.write('<scr'+'ipt type="text/javascript" src="axios/dist/axios.min.js" ></scr'+'ipt>');

(function (d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v3.1&appId=569283473507613";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


function checkAuth() {
    var auth = true;
    if (Cookies.get("id") == undefined) {
        auth = false;
    }
    return auth;
}

function clearAuth() {
    Cookies.remove("name");
    Cookies.remove("id");
    Cookies.remove('token');
    Cookies.remove("first");
}

function logout() {
    FB.getLoginStatus(function (response) {
        if (response.status === 'connected') {
            FB.logout(function (response) {
                
            });
        }
    });
}

function checkLoginState() {
    $('.ui.sidebar').sidebar('hide');
    FB.getLoginStatus(function (response) {
        console.log("STATUS:" + response.status)
        if (response.status == "connected") {
            var access_token = FB.getAuthResponse()['accessToken'];

            FB.api('/me?fields=id,name,email,birthday,devices,age_range', function (response) {
                console.log("Graph called finished :)")
                console.log(response);
                Cookies.set('name', response.name);
                Cookies.set('id', response.id);
                Cookies.set('token', access_token);
                Cookies.set("first","false")
                
                let data = new FormData();
                        data.append("user_id", response.id);
                        data.append("user_name", response.name);
                        data.append("email", response.email);
                        data.append("age", 20);
                        axios({
                            method: 'post',
                            url: 'http://askbox.com:9999/user/register',
                            data: data
                        }).then(function (response) {
                             if(response.data.data==0){
                                 $('.ui.first.modal').modal('show');
                                 $('.ui.second.modal').modal('attach events','#to_second','show')
                             }
                        });
                
                console.log("This is cookie");
                console.log(Cookies.get("api_url"))
                console.log(Cookies.get("name"));
                console.log(Cookies.get("id"));
                console.log(Cookies.get("token"));

                reloadProfile();
                

            }, {
                scope: 'email,birthday'
            });
        } else {
            
            clearAuth();
            reloadProfile();
        }
    });
}

function getHeader() {
    var header = {
        'token': Cookies.get("token"),
        'id': Cookies.get("id"),
        'name':Cookies.get("name")
    }
    return header;
}

function getProfileImage() {
    return "http://graph.facebook.com/" + Cookies.get("id") + "/picture?type=large";
}

function reloadProfile() {
    console.log("Profile Reloaded:" + getProfileImage());
    console.log("Check Auth:" + checkAuth());
    if (checkAuth()) {
        $("#username").html(Cookies.get("name"));
        $('#user_profile').attr("src", getProfileImage());
        
        
    } else {
                $("#username").html("Guest User");
        $('#user_profile').attr("src", "Images/avatar/large/daniel.jpg");
    }
}
<!--facebook script end-->