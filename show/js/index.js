let user = JSON.parse(userJson)
$('.avatar img').attr('src', user['iconUrl'])
$('.human .name').text(user['name'])
$('.human .time').text(user['created']+ ' 加入')
$('.user .introduce').text(user['intro'])

let notebooks = JSON.parse(notebooksJson)
let content = []
for (let notebook of notebooks) {
    if (!notebook['isExpired']) {
        continue;
    }

    let itemHtml = `<div class="item" data-id="${notebook['id']}">
            <div class="cover" style="background-image: url('${notebook['coverUrl']}')">
            </div>
            <div class="title">
                ${notebook['subject']}
            </div>
            <div class="time">
                <div class="start">
                    ${notebook['created']} 创建
                </div>
                <div class="end">
                    ${notebook['expired']} 过期
                </div>
            </div>
        </div>`

    content.push(itemHtml)
}
$('.notebooks').html(content.join(''))

$('.item').click(function () {
    window.location = 'notebook.html?id='+ $(this).data('id')
})