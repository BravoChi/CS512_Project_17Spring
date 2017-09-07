//heighlight left
var context = document.querySelector(".context",".context_entities"); // requires an element with class "context" to exist
var instance = new Mark(context);

for (each_keyword in data.highlight_term_list) {
    instance.mark(each_keyword,{"separateWordSearch":false, "element":"mark","className":each_keyword.1});
}
/*
{% for each_keyword in data.highlight_term_list %}
    instance.mark("{{ each_keyword }}",{"separateWordSearch":false, "element":"mark","className":"{{each_keyword.1}}"});
{% endfor %}

//no heighlight on author, journel, year line
{% for each_hit_dict in data.hits.hits %}
    var context = document.querySelector(".context_nohighlight_{{loop.index0}}",".context_entities"); // requires an element with class "context" to exist
    var instance = new Mark(context);
    {% for each_keyword in data.highlight_term_list %}
        instance.unmark("{{ each_keyword }}",{"separateWordSearch":false, "element":"mark","className":"{{each_keyword.1}}"});
    {% endfor %}
{% endfor %}

//heighlight right
var context = document.querySelector(".context_entities"); // requires an element with class "context" to exist
var instance = new Mark(context);
{% for each_keyword in data.highlight_term_list %}
    instance.mark("{{ each_keyword }}",{"separateWordSearch":false, "element":"mark","className":"{{each_keyword.1}}"});
{% endfor %}
*/