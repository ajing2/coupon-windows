/**
 * Request price information
 */

var BASE_URL = 'http://zhushou.huihui.cn/';
var ZERO = ["0", "00", "000", "0000", "00000", "000000", "0000000", "00000000"];
var CODE_OFFSET = 88;

var BROWSER = "chrome";
var VERSION = "4.2.9.2";
var VENDOR = "youdaonew";
var AV = "3.0";
var EXTENSION_ID = "370784ca-2839-e9f7-c0a7-20ad1a7a4ea4";
var EMAIL = "";
var POP = "";
var REQUEST_ID = "productSense";
var MSG = "";

var WUPI = "youdaogouwupi";
var JSONP = "jsonp";

function to(a, c) {
    var e = "" + (a + CODE_OFFSET).toString(16);
    var f = c - e.length;

    return f > 0 ? ZERO[f - 1] + e : e;
}

function isString(str) {
    return true; // toString.call(str) === '[object String]';
}

function strReverse(a) {
    var b, c = [];
    for (b = 0, l = a.length; b < l; b++) c[c.length] = a.charAt(b);
    return c.reverse().join("");
}

function encrypt(a, b, e) {
    var f, g = [];
    if (!isString(a)) return "";
    for (f = 0, l = a.length; f < l; f++) g[g.length] = to(a.charCodeAt(f), b);
    return e ? strReverse(g.join("")) : g.join("");
}

function decrypt(a, b, e) {
    if (!isString(a)) return "";
    var f = [];
    e && (a = strReverse(a));
    for (var g = 0, h = 0; g < a.length; g += b, h++) {
        var i = a.substring(g, g + b);
        f[h] = d.tranFormat(i, b)
    }
    return String.fromCharCode.apply(String, f);
}

function comboParams(params) {
    var i, group = [];
    for (i in params) {
        if (params.hasOwnProperty(i)) {
            var str = i + "=" + encodeURIComponent(params[i]);
            if (JSONP === i) {
                group.unshift(str);
            } else {
                group.push(str);
            }
        }
    }
    group.push("t=" + +new Date);
    return group.join("&")
}

function aJax(requestId, request) {
    var CALLBACK = "{$callback}";
    var jsonp = WUPI + +new Date;
    request[JSONP] = jsonp;

    var index = requestId.indexOf(CALLBACK);
    if (index > -1) {
        requestId = requestId.replace(CALLBACK, jsonp);
    }

    var url = BASE_URL + requestId + (requestId.indexOf("?") > -1 ? "&" : "?") + comboParams(request);
    return url.substr(0, 1900);
}

function requestPriceInfo(title, pageUrl) {
    var request = {};
    var group = ["t=" + title.substr(0, 250), "k=lxsx", "d=ls"];
    var encodedTitle = encrypt(group.join("^&"), 4, false);
    var encodedUrl = encrypt(pageUrl, 2, true);
    var len = 1900 - encodedUrl.length;

    encodedTitle = encodedTitle.length > len ? encodedTitle.substr(0, len) : encodedTitle;

    request.browser = BROWSER;
    request.version = VERSION;
    request.vendor = VENDOR;
    request.av = AV;
    request.extensionid = EXTENSION_ID;
    request.email = EMAIL;
    request.pop = POP;
    request.k = encodedTitle;
    request.nl = true;

    var uri = encodeURIComponent(pageUrl);
    var encodedUrl = encrypt(uri, 2, true);

    request.m = encodedUrl;
    request.msg = MSG;

    return aJax(REQUEST_ID, request);
}

