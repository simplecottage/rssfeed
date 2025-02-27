<script>
  import { onMount } from "svelte";
  import { syncService } from "../services/api";

  let syncKey = localStorage.getItem("syncKey") || "";
  let newSyncKey = "";
  let loading = false;
  let error = null;
  let message = null;

  onMount(() => {
    if (!syncKey) {
      generateSyncKey();
    }
  });

  async function generateSyncKey() {
    try {
      loading = true;
      error = null;
      message = null;

      const key = await syncService.getSyncKey();
      newSyncKey = key;
      loading = false;
    } catch (err) {
      error = err.message || "Failed to generate sync key";
      loading = false;
    }
  }

  async function saveSyncKey() {
    try {
      loading = true;
      error = null;
      message = null;

      // Check if the key exists
      try {
        await syncService.getSyncData(newSyncKey);
      } catch (err) {
        // If key doesn't exist, create it with current feeds
        const data = await syncService.exportFeeds();
        await syncService.updateSyncData(newSyncKey, { data });
      }

      // Save key to local storage
      localStorage.setItem("syncKey", newSyncKey);
      syncKey = newSyncKey;
      message = "Sync key saved successfully!";
      loading = false;
    } catch (err) {
      error = err.message || "Failed to save sync key";
      loading = false;
    }
  }

  async function exportFeeds() {
    try {
      loading = true;
      error = null;
      message = null;

      const result = await syncService.exportFeeds();

      // Create a download link
      const blob = new Blob([result.data], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "feeds-export.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      message = "Feeds exported successfully!";
      loading = false;
    } catch (err) {
      error = err.message || "Failed to export feeds";
      loading = false;
    }
  }

  async function syncFeeds() {
    if (!syncKey) {
      error = "No sync key set. Please set a sync key first.";
      return;
    }

    try {
      loading = true;
      error = null;
      message = null;

      // Get data from server
      const data = await syncService.getSyncData(syncKey);

      // Import feeds
      await syncService.importFeeds(data.data);

      message = "Feeds synchronized successfully!";
      loading = false;
    } catch (err) {
      error = err.message || "Failed to sync feeds";
      loading = false;
    }
  }

  let fileInput;

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        loading = true;
        error = null;
        message = null;

        const content = e.target.result;
        await syncService.importFeeds(content);

        message = "Feeds imported successfully!";
        loading = false;
      } catch (err) {
        error = err.message || "Failed to import feeds";
        loading = false;
      }
    };

    reader.readAsText(file);
  }
</script>

<div class="space-y-6">
  <div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
        sync settings
      </h3>
      <div class="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
        <p>
          use a sync key to synchronize your feeds across devices without
          authentication. keep this key private and use it on all your devices.
        </p>
      </div>

      {#if error}
        <div class="mt-4 px-4 py-3 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      {/if}

      {#if message}
        <div class="mt-4 px-4 py-3 bg-green-50 text-green-700 rounded-md">
          {message}
        </div>
      {/if}

      <div class="mt-5">
        {#if syncKey}
          <div class="mb-4">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
              current sync key:
            </p>
            <div class="mt-1 flex rounded-md shadow-sm">
              <input
                type="text"
                readonly
                value={syncKey}
                class="flex-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full min-w-0 rounded-md sm:text-sm border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
              <button
                type="button"
                on:click={() => navigator.clipboard.writeText(syncKey)}
                class="ml-3 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                copy
              </button>
            </div>
          </div>
        {/if}

        <div class="mb-4">
          <label
            for="new-sync-key"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {syncKey ? "new sync key:" : "set sync key:"}
          </label>
          <div class="mt-1 flex rounded-md shadow-sm">
            <input
              type="text"
              id="new-sync-key"
              bind:value={newSyncKey}
              placeholder="Enter or generate a sync key"
              class="flex-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full min-w-0 rounded-md sm:text-sm border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <button
              type="button"
              on:click={generateSyncKey}
              disabled={loading}
              class="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              generate
            </button>
          </div>
        </div>

        <div class="flex space-x-3">
          <button
            type="button"
            on:click={saveSyncKey}
            disabled={loading || !newSyncKey}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? "saving..." : "save key"}
          </button>

          <button
            type="button"
            on:click={syncFeeds}
            disabled={loading || !syncKey}
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {loading ? "syncing..." : "sync feeds"}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
        export and import
      </h3>
      <div class="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
        <p>backup your feeds or import from another source.</p>
      </div>

      <div class="mt-5 flex space-x-3">
        <button
          type="button"
          on:click={exportFeeds}
          disabled={loading}
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? "exporting..." : "export feeds"}
        </button>

        <input
          type="file"
          accept=".json"
          on:change={handleFileSelect}
          bind:this={fileInput}
          class="hidden"
        />

        <button
          type="button"
          on:click={() => fileInput.click()}
          disabled={loading}
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600 disabled:opacity-50"
        >
          {loading ? "importing..." : "import feeds"}
        </button>
      </div>
    </div>
  </div>
</div>
