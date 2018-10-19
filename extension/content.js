
var url;
var address_2;

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

function onSuccess(data, contact_info, addr_1, addr_2) {
    var strings = create_route_strings(data);
    var ele = "<div>" + addr_1 + ' -> ' + addr_2 + ': <br>'
    for (var i = 0; i < strings.length; i++) {
        ele += strings[i] + '<br>'
    }
    ele += "</div>"
    $(contact_info).append(ele)
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
            if (cls != "ad_iframe") {
                return;
            }

            setTimeout(function() {
                var iframe = $(node).find("iframe")[0];
                var iframe_document = iframe.contentWindow.document
                var details = $(iframe_document).find("div.details_block_body")[0]
                var contact_info = $(iframe_document).find("div.details_block_body")[2]
                var city = $(details).find("div tr td")[3].innerText.trim()
                var street = $(details).find("div tr td")[9].innerText.split(" ").slice(0, -1).join(" ").trim()
                var address_1 = street + ',' + city;
                console.log("requiring routes:", address_1, address_2)
                $.ajax({
                        type: 'GET',
                        url: url,
                        data: {
                            'src_addr': address_1,
                            'dst_addr': address_2
                        },
                        dataType: "json",
                        success: function(response) {
                            onSuccess(response, contact_info, address_1, address_2);
                        },
                        error: function(request, status, error) {
                            console.log(request, status. errror);
                        }
                });
            }, 2500);
        }
    });
});

fetch(chrome.runtime.getURL("config"))
    .then(function(response) {
        return response.json().then(function(json) {
            address_2 = json["location"],
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
