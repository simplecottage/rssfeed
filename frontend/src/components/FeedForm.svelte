<script>
  import { onMount } from "svelte";
  import { useNavigate, useParams } from "svelte-navigator";
  import { feedService } from "../services/api";

  const navigate = useNavigate();
  const params = useParams();

  let feed = {
    title: "",
    url: "",
    description: "",
  };

  let loading = false;
  let error = null;
  let isEditMode = false;

  onMount(async () => {
    const feedId = $params.id;

    if (feedId) {
      isEditMode = true;
      loading = true;

      try {
        feed = await feedService.getById(feedId);
        loading = false;
      } catch (err) {
        error = err.message || "Failed to load feed details";
        loading = false;
      }
    }
  });

  async function handleSubmit() {
    loading = true;
    error = null;

    try {
      if (isEditMode) {
        await feedService.update($params.id, feed);
      } else {
        await feedService.create(feed);
      }

      navigate("/");
    } catch (err) {
      error = err.message || "Failed to save feed";
      loading = false;
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg">
  <div class="px-4 py-5 sm:p-6">
    <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
      {isEditMode ? "edit feed" : "add new feed"}
    </h3>

    {#if error}
      <div class="mt-4 px-4 py-3 bg-red-50 text-red-700 rounded-md">
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="mt-5 space-y-6">
      <div>
        <label
          for="title"
          class="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          title
        </label>
        <div class="mt-1">
          <input
            type="text"
            name="title"
            id="title"
            bind:value={feed.title}
            required
            class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="feed title"
          />
        </div>
      </div>

      <div>
        <label
          for="url"
          class="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          feed url
        </label>
        <div class="mt-1">
          <input
            type="url"
            name="url"
            id="url"
            bind:value={feed.url}
            required
            class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="https://example.com/feed.xml"
          />
        </div>
      </div>

      <div>
        <label
          for="description"
          class="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          description (optional)
        </label>
        <div class="mt-1">
          <textarea
            name="description"
            id="description"
            bind:value={feed.description}
            rows="3"
            class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="a brief description of this feed"
          ></textarea>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          type="button"
          on:click={() => navigate("/")}
          class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
        >
          cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if loading}
            saving...
          {:else}
            {isEditMode ? "update feed" : "add feed"}
          {/if}
        </button>
      </div>
    </form>
  </div>
</div>
