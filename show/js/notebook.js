const urlParams = new URLSearchParams(window.location.search);
const notebookId = urlParams.get('id')

let user = JSON.parse(userJson)
$('.avatar img').attr('src', user['iconUrl'])
$('.human .name').text(user['name'])
$('.human .time').text(user['created']+ ' 加入')
$('.user .introduce').text(user['intro'])

let notebookDetails = JSON.parse(notebookDetailsJson)
let currDetails = notebookDetails[notebookId]
let content = []
for (let detail of currDetails) {
    let itemHtml = `<div class="item">
            <div class="title">
                《${detail['notebook_subject']}》 ${detail['created']}
            </div>
            <pre class="content">${detail['content']}</pre>`

    if (detail['photoUrl']) {
        itemHtml += `<div class="visual">
                <img src="${detail['photoUrl']}" />
            </div>`
    }
    itemHtml += '</div>'

    content.push(itemHtml)
}

$('.list').html(content.join(''))
