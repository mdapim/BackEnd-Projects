// window.onload = async function load() {
//   getStories()
// }

window.onload = async function load() {
  getStories()
  document
    .getElementById('submit-search')
    .addEventListener('click', onSearchClick())
}

async function getStories() {
  const res = await fetch(`/stories`, {
    method: 'GET',
    credentials: 'include'
  })
  const data = await res.json()

  displayStories(data['stories'])
}

async function handleVote(e) {
  const elemID = e.target.id.split('-')
  const id = elemID[0]
  const direction = elemID[1]
  const rawRes = await fetch(`/stories/${id}/votes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction }),
    credentials: 'include'
  })
  const res = await rawRes.json()
  location.reload()
}

function displayStories(stories) {
  stories.forEach(createStory)
}

function createStory(story) {
  const stories = document.getElementById('stories')
  const storyWrapper = document.createElement('div')
  storyWrapper.id = 'story'

  if (story.score == 1) {
    storyWrapper.innerHTML = `
	<p id="story1">
		<a class="title" href=${story.url}>${story.title} </a>
		<span>(${story.score} point)</span>

	</p>`
  } else {
    storyWrapper.innerHTML = `
	<p id="story1">
		<a class="title" href=${story.url}>${story.title} </a>
		<span>(${story.total_votes} points)</span>

	</p>`
  }

  const upvoteButton = createVoteButton('upvote', `${story.id}-up`, '⬆')
  const downvoteButton = createVoteButton('downvote', `${story.id}-down`, '⬇')

  storyWrapper.append(upvoteButton, downvoteButton)
  stories.append(storyWrapper)
}

function createVoteButton(className, id, text) {
  const button = document.createElement('button')
  button.id = id
  button.className = className
  button.addEventListener('click', handleVote)
  button.innerText = text
  return button
}

async function onSearchClick() {
  const searchInputText = document.getElementById('search').value
  console.log('js log', searchInputText)

  // const res = await fetch(
  //   `http://127.0.0.1:5000/stories?title=${searchInputText}`,
  //   {
  //     method: 'GET',
  //     credentials: 'include'
  //   }
  // )
  // const data = await res.json()
  // displayStories(data['stories'])
  return `http://127.0.0.1:5000/searches?title=${searchInputText}`
}
