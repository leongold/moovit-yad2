
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
    if ("error" in data) {
        $(contact_info).append(
            "<div>" + data["error"] + "</div>"
        )
        return;
    }
    var strings = create_route_strings(data["routes"]);
    var ele = "<div>" + data["date"] + "<br>";
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
                var details_items = $(details).find("div tr")
                var contact_info = $(iframe_document).find("div.details_block_body")[2]
                for (i=0; i < details_items.length-1; i++) {
                    var items = $(details_items[i]).find("td");
                    var key = items[0].innerText;
                    if (key.includes("ישוב")) {
                        var city = items[1].innerText.trim();
                    }
                    else if (key.includes("כתובת")) {
                        var street = items[1].innerText.trim();
                    }
                }
                var address_1 = street + ',' + city;
                var address_2 = $(document).find("input[id=dst]").val() || $(document).find("input[id=dst]").attr("placeholder");
                console.log("requiring routes:", address_1, address_2)
                $.ajax({
                        type: 'GET',
                        url: $(document).find("input[id=url]").val() || $(document).find("input[id=url]").attr("placeholder"),
                        data: {
                            'src_addr': address_1,
                            'dst_addr': address_2,
                        },
                        dataType: "json",
                        success: function(response) {
                            onSuccess(response, contact_info, address_1, address_2);
                        },
                        error: function(request, status, error) {
                            console.log(request, status, error);
                        }
                });
                $(contact_info).append("<div>טוען מסעות עבור " + address_1 + " -> " + address_2 + "...</div>");
            }, 2500);
        }
    });
});

var config = {
    attributes: false,
    childList: true,
    characterData: false,
    subtree: true
};

observer.observe(document.body, config);

var tbl = $($(document).find("div.mainTable_top_right td[align=left] tr")[0])
tbl.append($('<td><form>url<input type="text" placeholder="http://104.248.143.170:5000" id="url"></form></td>'))
tbl.append($('<td><form>dst<input type="text" placeholder="דרך ירושליים 34,רעננה" id="dst"></form></td>'))

var url = $(document).find("input[id=url]")
$(url).on("input", function() { 
    var value = $(document).find("input[id=url]").val();
    chrome.storage.local.set({ "url-input": value }, function () {});
});
chrome.storage.local.get(["url-input"], function (result) {
    $(url).val(result["url-input"] || $(url).attr("placeholder"))
});

dst = $(document).find("input[id=dst]")
$(dst).on("input", function () {
    var value = $(document).find("input[id=dst]").val();
    chrome.storage.local.set({ "dst-input": value }, function () {});
});
chrome.storage.local.get(["dst-input"], function (result) {
    $(dst).val(result["dst-input"] || $(dst).attr("placeholder"))
});
