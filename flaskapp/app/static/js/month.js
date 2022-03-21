
$(document).ready(function() {
    var table = new Tabulator("#table", {
        height: 800,
        layout: "fitDataFill",
        movableColumns: true,
        selectable: 1,
        columns: [
            {title: "Id", field: "id"},
            {title: "Date", field: "date", formatter:'datetime', formatterParams:{outputFormat: 'YYYY-MM-DD'}},
            {title: "Account", field: "account"},
            {title: "Description", field: "description"},
            {title: "Amount", field: "amount", align: 'right', formatter:'money', bottomCalc:'sum', bottomCalcParams: {precision: 2}},
            {title: "Tags", field: "tags"},
        ],
        rowClick:function(e, row) {
            $("#display_transaction_id").html(row.getData().id);
            $("#transaction_id").val(row.getData().id);
            var tag_string = row.getData().tags;
            if (tag_string) {
                $("#tags").val(tag_string + ",");
            } else {
                $("#tags").val("");
            }

            $("#tag_transaction").removeClass('no_display');
            $("#tags").focus();
        },
        rowContext: function(e, row) {
            e.preventDefault();// Prevents the browser context menu from appearing
            console.log(row.getData().id);
            $("#transaction_id").val(row.getData().id);
            $("#transaction_id_remove_tag").html(row.getData().id);
            $("#tags_to_remove").empty();
            var tag_string = row.getData().tags;
            var tags = tag_string.split(',');
            for (i = 0; i < tags.length; i++) {
                $("#tags_to_remove").append('<option value="'+tags[i]+'">'+tags[i]+'</option>');
            }
            $("#remove_tag").removeClass('no_display');

            $("#tags_to_remove").change(function() {
                var tag = $(this).children(":selected").html();
                var t_id = $("#transaction_id").val();
                var ajax_url = "/analysis/ajax/removetag/"+t_id+"/"+tag+"/";
                $("#remove_tag").addClass('no_display');
                $.get(ajax_url, function( data ) {
                    if (data['status'] == 'success') {
                        table.updateData([{id: $("#transaction_id").val(), tags: data['tag_string']}]);
                    }
                    $("#transaction_id").val('');
                    $("#tags_to_remove").empty();
                });
            });

            console.log(tags);

        }
    });
    $.get('/api/tags/', function(tags) {
        tags = JSON.parse(tags);
        var availableTags = tags.map(function(v) { return v.name; });
        function split( val ) {
            return val.split( /,\s*/ );
        }
        function extractLast( term ) {
            return split( term ).pop();
        }

        $( "#tags" )
        // don't navigate away from the field on tab when selecting an item
            .on( "keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                    $( this ).autocomplete( "instance" ).menu.active ) {
                    event.preventDefault();
                }
            })
            .autocomplete({
                minLength: 0,
                source: function( request, response ) {
                    // delegate back to autocomplete, but extract the last term
                    response( $.ui.autocomplete.filter(
                        availableTags, extractLast( request.term ) ) );
                },
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function( event, ui ) {
                    var terms = split( this.value );
                    // remove the current input
                    terms.pop();
                    // add the selected item
                    terms.push( ui.item.value );
                    // add placeholder to get the comma-and-space at the end
                    terms.push( "" );
                    this.value = terms.join( "," );
                    return false;
                }
            });
        $("#btn_tag_transaction").click(function() {
            var api_url = "/api/tagtransaction/";
            api_url += $("#transaction_id").val() + "/";
            api_url += $("#tags").val();
            $.get(api_url, function( data ) {
                $("#tags").val('');
                if (data['status'] == 'success') {
                    table.updateData([{id: $("#transaction_id").val(), tags: data['tag_string']}]);
                }
                $("#tag_transaction").addClass('no_display');
                //$("#status_message").html("File import into account: "+ data['account'] + "<br>Status: " + data['status']);
            });
        });
        $("#btn_cancel_tag").click(function() {
            $("#tag_transaction").addClass('no_display');
        });
        $("#btn_cancel_remove").click(function() {
            $("#remove_tag").addClass('no_display');
        });

    } );

    $("#autotag_button").click(function() {
        var ajax_url = "/analysis/ajax/autotag/";
        ajax_url += $("#id_month_date").val() + "/";
        $.get(ajax_url, function( data ) {
            console.log(data);
        });
    });
    $.get("/api/month/"+$("#start_date").val(), function(data) {
        table.setData(data);
        console.log(typeof(data));
    })
});
