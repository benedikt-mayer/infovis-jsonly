$(function () {
    fetchAsync("http://127.0.0.1:5002/");
});

async function fetchAsync(url) {
    let response = await fetch(url, {
        mode: 'cors'
    });
    let data = await response.json();
    $("#placeholder").text(data);
}