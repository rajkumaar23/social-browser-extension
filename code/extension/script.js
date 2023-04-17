window.addEventListener('load', function() {
  updateInterface(JSON.parse(localStorage.getItem('recommendationsObject')));
});

const submitBtn = document.querySelector('#submitBtn');
submitBtn.addEventListener('click', async () => {
  const historyUrls = await getHistoryUrls();
  const loading = document.querySelector('#loading');
  loading.style.display = 'block';
  const recommendations = await getRecommendations(historyUrls);
  localStorage.setItem('recommendationsObject', JSON.stringify(recommendations));
  updateInterface(recommendations);
  loading.style.display = 'none';
});

async function getHistoryUrls() {
  return new Promise((resolve) => {
    chrome.history.search({
      text: '',
      maxResults: 5,
      startTime: 1586997176000
    }, (historyItems) => {
      const historyUrls = historyItems.map((item) => item.url);
      console.log(historyUrls);
      resolve(historyUrls);
    });
  });
}

async function getRecommendations(historyUrls) {
  const requestBody = JSON.stringify({ history: historyUrls });
  const response = await fetch('http://localhost:8000/recommendations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: requestBody
  });
  const responseBody = await response.json();
  return responseBody.recommendations;
}

function updateInterface(recommendations) {
  const recommendationsDiv = document.querySelector('#recommendations');
  recommendationsDiv.style.padding = '20px';
  recommendationsDiv.innerHTML = '<h3 class="title is-3 has-text-centered">URL Recommendations</h3>';
  const ul = document.createElement('ul');
  ul.style.listStyleType = 'auto';
  recommendations.forEach((url) => {
    const li = document.createElement('li');
    li.classList.add('is-size-6');
    li.innerHTML = (`<a href='${url['url']}' class='has-text-link' target='_blank'>${url['title']}</a>`);
    ul.appendChild(li);
  });
  recommendationsDiv.appendChild(ul);
  recommendationsDiv.classList.remove("is-hidden");
}
