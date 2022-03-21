
$(document).ready(function() {
    var table = new Tabulator("#table", {
        height: 600,
        columns: [
            {
                title: "Month",
                field: "effective_month",
            },
        ],
        rowClick: function(e, row) {
            var url = "/month/" + row.getData().effective_month;
            console.log(url);
            window.location = url;
        },
    });
    $.get("/api/months", function(data) {
        table.setData(data);
    })
});
