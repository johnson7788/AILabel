<template>
  <div class="searchbox-form" role="search">
    <input class="search-input" type="search" placeholder="Ask me anything..." aria-label="Enter your search here" />
    <div class="clear-icon">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"
        class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
      </svg>
      <a href="javascript:void(0);" aria-label="Clear text" role="button"></a>
    </div>
    <div class="mic-icon" role="button" aria-label="Search using voice">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"
        class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.searchbox-form {
  display: inline-block;
  background-color: #fff;
  color: #71777d;
  font: 18px 'Microsoft YaHei', Arial, sans-serif;
  border-radius: 24px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.05), 0 2px 4px 1px rgba(0, 0, 0, 0.09);
  position: relative;
}

.search-input {
  display: inline-block;
  border: none;
  outline: none;
  padding: 0 10px;
  flex: 1;
}

.clear-icon,
.mic-icon {
  display: inline-block;
  margin: 3px 10px;
  cursor: pointer;
  vertical-align: middle;
}
</style>
