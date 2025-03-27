document.getElementById("commentForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form submission

    const commentInput = document.getElementById("commentInput");
    const commentText = commentInput.value;
    const date = new Date().toLocaleString(); // Get current date and time

    // Create a new comment element
    const commentElement = document.createElement("div");
    commentElement.classList.add("comment");
    commentElement.innerHTML = `<p>${commentText}</p><p class="date">${date}</p>`;

    // Append the new comment to the comment list
    document.getElementById("commentList").appendChild(commentElement);

    // Clear the input field
    commentInput.value = '';
});