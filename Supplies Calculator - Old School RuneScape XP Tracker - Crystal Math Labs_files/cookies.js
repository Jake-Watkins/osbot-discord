function get_cookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return false;
} 


function set_cookie(cname, cvalue, exdays, path=null) {
	var d = new Date();
	d.setTime(d.getTime() + (exdays*24*60*60*1000));
	var expires = "expires="+ d.toUTCString();
	document.cookie = cname + "=" + cvalue + "; " + expires + (path ? "; path=" + path : '');
} 

function add_filter_to_url(anchor) {
	var cookie = get_cookie('filter');
	var href = anchor.getAttribute('href');
	if(cookie) {
		cookie = cookie.replace('%2C', ',');
		if(cookie != 'onhiscores') {
			anchor.setAttribute('href', href + '?filter=' + decodeURIComponent(cookie));
		}
	} else {
		if(href == 'halloffame.php') {
			anchor.setAttribute('href', href + '?filter=');
		}
	}
	anchor.removeAttribute('onmouseover');
}

var pat = new RegExp("(tracker[\-A-Za-z0-9]*)\/");
var result = pat.exec(window.location.href);
if(result) {
	set_cookie('tracker', result[1], 31, '/');
}

String.prototype.ucwords = function() {
	str = this.toLowerCase();
	return str.replace(/(^([a-zA-Z\p{M}]))|([ -][a-zA-Z\p{M}])/g,
		function($1){
		    return $1.toUpperCase();
		});
}
