const limit = 10;
$(".imgAdd").click(function () {
    if ($(this).closest(".repeatme").find(".form-inline").length < limit) {
        var oldrow = $(this).closest(".repeatme").find(".form-inline").last();
        var row = oldrow.clone(true, true);
        var elem_id = row.find(":input")[0].id;
        var elem_num = parseInt(elem_id.replace(/(.*)-(\d{1,2})/m, '$2')) + 1;  
        row.children(":input").each(function() {
            var id = $(this).attr("id").replace(/(.*)-(\d{1,2})-(.*)/, '$1'+'-'+(elem_num)+'-'+'$3');
            $(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
        });
        row.children("label").each(function() {
            var id = $(this).attr("for").replace(/(.*)-(\d{1,2})-(.*)/, '$1'+'-'+(elem_num)+'-'+'$3');
            $(this).attr('for', id);
        });
        $(this).closest(".repeatme").find('.imgAdd').before(row);
    }
});
$(document).on("click", "i.del", function () {
    if ($(this).closest(".repeatme").find(".form-inline").length > 1) {
        $(this).parent().remove();
    }
});
/* no need this now
$('select[id$="grade"]').change(function () {
    // above find id, which ends with grade: $=
    // find out 'Dump' and 'dumpster', make sure they exist in grade, customer
    // Dump and dumpster, case sensitive
    var gradeid = $(this).attr('id');
    // get the value of this $gradeid option Dump
    var v = $('#' + gradeid).find('option:contains("Dump")').val();
    if ($(this).val() == v) {
        var customerid = gradeid.replace(/(.*)-grade/, '$1'+'-customer');
        var cv = $('#' + customerid).find('option:contains("dumpster")').val();
        $('#' + customerid).val(cv);
    }
});
*/