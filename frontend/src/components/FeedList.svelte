<script>
  import { onMount } from "svelte";
  import { Link, navigate } from "svelte-navigator";
  import { feedService } from "../services/api";

  let feeds = [];
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      feeds = await feedService.getAll();
      loading = false;
    } catch (err) {
      error = err.message || "Failed to load feeds";
      loading = false;
    }
  });

  async function refreshFeeds() {
    try {
      loading = true;
      await feedService.refresh();
      feeds = await feedService.getAll();
      loading = false;
    } catch (err) {
      error = err.message || "Failed to refresh feeds";
      loading = false;
    }
  }

  async function deleteFeed(id) {
    if (confirm("Are you sure you want to delete this feed?")) {
      try {
        await feedService.delete(id);
        feeds = feeds.filter((feed) => feed.id !== id);
      } catch (err) {
        error = err.message || "Failed to delete feed";
      }
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
  <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
    <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
      your feeds
    </h3>
    <button
      class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      on:click={refreshFeeds}
      disabled={loading}
    >
      {#if loading}
        refreshing...
      {:else}
        refresh all
      {/if}
    </button>
  </div>

  {#if error}
    <div class="px-4 py-3 bg-red-50 text-red-700 border-t border-red-200">
      {error}
    </div>
  {/if}

  {#if loading && feeds.length === 0}
    <div class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
      loading feeds...
    </div>
  {:else if feeds.length === 0}
    <div class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
      <p>no feeds yet</p>
      <p class="mt-2">
        <Link to="/feeds/new" class="text-indigo-600 hover:text-indigo-500">
          add your first feed
        </Link>
      </p>
    </div>
  {:else}
    <ul class="divide-y divide-gray-200 dark:divide-gray-700">
      {#each feeds as feed (feed.id)}
        <li class="px-4 py-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-700">
          <div class="flex items-center justify-between">
            <div class="truncate">
              <Link
                to={`/feeds/${feed.id}`}
                class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium"
              >
                {feed.title}
              </Link>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 truncate">
                {feed.url}
              </p>
            </div>
            <div class="ml-2 flex-shrink-0 flex">
              <button
                on:click={() => deleteFeed(feed.id)}
                class="ml-2 p-1 rounded-full text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <span class="sr-only">delete</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
              <Link
                to={`/feeds/${feed.id}/edit`}
                class="ml-2 p-1 rounded-full text-gray-400 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <span class="sr-only">edit</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </Link>
            </div>
          </div>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            last updated: {new Date(feed.last_updated).toLocaleString()}
          </p>
        </li>
      {/each}
    </ul>
  {/if}
</div>
