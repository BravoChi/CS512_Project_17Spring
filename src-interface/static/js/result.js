/* Highlight by Keywords */
function highlightKeyword(data) {

    // highlight left
    var context = document.querySelector(".context");
    var instance = new Mark(context);  
    for (i = 0; i < data.highlight_term_list.length; i ++) {
        var each_keyword = data.highlight_term_list[i]
        instance.mark(each_keyword, {"separateWordSearch":false, "element":"mark", "className":each_keyword});
    }  

    // no highlight on author, journal, year line
    for (i = 0; i < data.hits.hits.length; i ++) {
        each_hit_dict = data.hits.hits[i];
        var context = document.querySelector(".context_nohighlight_" + i);
        var instance = new Mark(context);
        for (j = 0; j < data.highlight_term_list.length; j ++) {
            var each_keyword = data.highlight_term_list[i];
            instance.unmark(each_keyword, {"separateWordSearch":false, "element":"mark", "className":each_keyword});
        }
    }

    // highlight right
    var context = document.querySelector(".context_entities");
    var instance = new Mark(context);
    for (i = 0; i < data.highlight_term_list.length; i ++) {
        each_keyword = data.highlight_term_list[i];
        instance.mark(each_keyword, {"separateWordSearch":false, "element":"mark", "className":each_keyword});
    }
}

/* Highlight by Entity */
function highlightEntity(data) {

    // achieve keyword vs. css_style (peusdo generation now)
    var keywords = data.highlight_term_list;
    var entities = [];
    var classLeft = [];
    var classRight = [];
    var count = [];
    for (i = 0; i < keywords.length; i ++) {
        if (Math.random() < 0.5) {
            entities.push('entity-red');
            classLeft.push('disease-red');
            classRight.push('label label-danger');
            count.push(parseInt(Math.random() * 500, 10));
        }
        else {
            entities.push('entity-blue');
            classLeft.push('gene-blue');
            classRight.push('label label-primary');
            count.push(parseInt(Math.random() * 500, 10));
        }
    }

    // hightlight left
    var context = document.querySelector(".context");
    var instance = new Mark(context);  
    for (i = 0; i < data.highlight_term_list.length; i ++) {
        var each_keyword = data.highlight_term_list[i]
        instance.mark(each_keyword, {"separateWordSearch":false, "element":"span", "className":classLeft[i]});
    }

    // no highlight on author, journal, year line
    for (i = 0; i < data.hits.hits.length; i ++) {
        each_hit_dict = data.hits.hits[i];
        var context = document.querySelector(".context_nohighlight_" + i);
        var instance = new Mark(context);
        for (j = 0; j < data.highlight_term_list.length; j ++) {
            var each_keyword = data.highlight_term_list[i];
            instance.unmark(each_keyword, {"separateWordSearch":false, "element":"span", "className":classLeft[i]});
        }
    }

    // add frequent entities in top results
    var div = document.getElementById('right-col');
    var entityList = findEntityList(entities);
    var newHTML = '';
    for (i = 0; i < entityList.length; i ++) {
        newHTML += '<ul class="list-group">';
        var entity = entityList[i];
        newHTML += '<li class="list-group-item list-group-item-info active" href="#">\
                        <b>Frequent ' + entity + ' entities in top results </b>\
                    </li>' 
        for (j = 0; j < entities.length; j ++) {
            if (entities[j] == entity) {
                newHTML += '<li class="list-group-item" href="#">\
                                <span class="badge">' + count[j] + '</span>' + keywords[j] +
                            '</li>'
            }
        }
        newHTML += '</ul>'
    }
    div.innerHTML = newHTML;
    console.log(div);

    // highlight right
    var context = document.querySelector(".context_entities");
    var instance = new Mark(context);
    for (i = 0; i < data.highlight_term_list.length; i ++) {
        each_keyword = data.highlight_term_list[i];
        instance.mark(each_keyword, {"separateWordSearch":false, "element":"span", "className":classRight[i]});
    }
}

function findEntityList(entities) {
    var entityList = [];
    for (i = 0; i < entities.length; i ++) {
        if (!entityList.includes(entities[i]))
            entityList.push(entities[i]);
    }
    return entityList;
}


