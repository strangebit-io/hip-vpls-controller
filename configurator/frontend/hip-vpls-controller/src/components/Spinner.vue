<template>
  <div class="modal-mask">
    <div class="spinner">
      <img src="@/assets/spinner.gif" />
    </div>
  </div>
</template>

<script>
export default {
  name: "Spinner",
  props: [],
  data() {
    return {};
  },
  methods: {},
  mounted() {},
};
</script>

<style scoped>
.modal-mask {
  position: fixed;
  z-index: 100009;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  transition: opacity 0.3s ease;
}

.spinner {
  position: absolute;
  bottom: calc(50%);
  right: calc(50% - 30px);
}
</style>
