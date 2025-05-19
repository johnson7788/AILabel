<template>
  <div
    class="flex items-center bg-white text-gray-500 text-[18px] font-sans rounded-full shadow-sm relative w-full max-w-lg"
    role="search"
  >
    <input
      class="flex-1 border-none outline-none px-4 py-2 rounded-full"
      type="search"
      placeholder="Ask me anything..."
      aria-label="Enter your search here"
    />
    <div class="flex items-center space-x-2 pr-4">
      <div class="cursor-pointer" aria-label="Clear text" role="button">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <div class="cursor-pointer" role="button" aria-label="Search using voice">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
          />
        </svg>
      </div>
    </div>
  </div>
</template>
