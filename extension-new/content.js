
var url;
var address_2;

function get_city(ele) {
    return ele.find("span.subtitle")[0].innerText.split(",").pop().trim()
}

function get_street(ele) {
    return $(ele.find("span.title")[0]).clone().children().remove().end().text().trim()
}

function create_route_strings(data) {
    var strings = [];
    for (var i = 0; i < data.length; i++) {
        var route = data[i];
        var total_time = route[0];
        var result = "זמן כולל: " + total_time + " דקות. מסע: ";
        for (var j = 0; j < route[1].length; j++) {
            var type = route[1][j][0];
            var attr = route[1][j][1];
            if (type == 'walk') {
                result += "צעד " + attr + " דקות";
            }
            else if (type == 'bus') {
                result += "אוטובוס קו " + attr;
            }
            else {
                result += "רכבת";
            }
            if (j != route[1].length-1) {
                result += ', ';
            } else {
                result += '.';
            }
        }
        strings.push(result);
    }
    return strings;
}

function append_routes(node, strings) {
    var content_ele = $(node.find("div.content")[2]);
    content_ele.append("<br/");
    for (var i = 0; i < strings.length; i++) {
        content_ele.append("<br/>" + strings[i]);
    }
}

function onSuccess(data, node) {
    var strings = create_route_strings(data);
    append_routes(node, strings);
}

var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes && mutation.addedNodes.length > 0) {
            var node = mutation.addedNodes[0];
        	try {
                var cls = node.getAttribute("class");
            } catch(err) {
            	return;
            }
            if (cls != "accordion_wide open") {
            	return;
            }

            var parent = $(node.parentElement);
            var city = get_city(parent);
            var street = get_street(parent);
            var address_1 = street + ',' + city;

            $.ajax({
                    type: 'GET',
                    url: url,
                    data: {
                        'src_addr': address_1,
                        'dst_addr': address_2
                    },
                    dataType: "json",
                    success: function(response) {
                        onSuccess(response, $(node));
                    },
                    error: function(request, status, error) {
                        console.log(request, status. errror);
                    }
            });
        }
    });
});

fetch(chrome.runtime.getURL("config"))
    .then(function(response) {
        return response.json().then(function(json) {
            address_2 = json["dst_address"],
            url = json["url"]
        }) 
    })

var config = {
    attributes: false,
    childList: true,
    characterData: false,
    subtree: true
};

observer.observe(document.body, config);
