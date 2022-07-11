let lastCommentContent = null;

function submitComment(endpoint) {
    const commentBody = document.getElementById("commentBody").value;
    if (commentBody != lastCommentContent && commentBody.length > 0) {
        lastCommentContent = commentBody;
        let request = new XMLHttpRequest();

        request.onreadystatechange = function() {
            if (this.readyState == 3 && this.status == 200) {
                const noCommentMessage = document.getElementById("no-comment-message");
                if (noCommentMessage != undefined) {
                    noCommentMessage.remove();
                }

                const commentsArea = document.getElementById("commentsArea");
                let element = document.createElement("div");
                element.innerHTML = this.responseText;
                commentsArea.appendChild(element, commentsArea.childNodes[0]);
            }
        };

        request.open("POST", endpoint, true);
        request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify(
            {
                "commentBody": commentBody
            }
        ));
    }
}