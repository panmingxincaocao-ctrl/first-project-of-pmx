const API_BASE = "http://localhost:8000";
let authToken = "";

const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const courseForm = document.querySelector("#course-form");
const progressForm = document.querySelector("#progress-form");
const refreshButton = document.querySelector("#refresh-courses");

const loginStatus = document.querySelector("#login-status");
const registerStatus = document.querySelector("#register-status");
const courseStatus = document.querySelector("#course-status");
const progressStatus = document.querySelector("#progress-status");
const courseList = document.querySelector("#course-list");

const showStatus = (element, message, isError = false) => {
  element.textContent = message;
  element.classList.toggle("error", isError);
};

const request = async (path, options = {}) => {
  const headers = options.headers || {};
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
};

const renderCourses = (courses) => {
  courseList.innerHTML = "";
  if (!courses.length) {
    courseList.textContent = "暂无课程";
    return;
  }
  courses.forEach((course) => {
    const card = document.createElement("article");
    card.className = "course-item";
    card.innerHTML = `
      <h3>${course.title}</h3>
      <p>${course.description}</p>
      <div class="meta">教师：${course.teacher}</div>
      <div class="meta">状态：${course.status}</div>
    `;
    courseList.appendChild(card);
  });
};

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  try {
    const data = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
    });
    authToken = data.token;
    showStatus(loginStatus, `登录成功，角色：${data.role}`);
  } catch (error) {
    showStatus(loginStatus, error.message, true);
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  try {
    const data = await request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
    });
    showStatus(registerStatus, `注册成功，ID：${data.id}`);
  } catch (error) {
    showStatus(registerStatus, error.message, true);
  }
});

courseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(courseForm);
  try {
    const data = await request("/api/courses", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
    });
    showStatus(courseStatus, `创建课程成功，ID：${data.id}`);
  } catch (error) {
    showStatus(courseStatus, error.message, true);
  }
});

progressForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(progressForm);
  try {
    const data = await request("/api/progress", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
    });
    showStatus(progressStatus, `提交成功，进度 ID：${data.id}`);
  } catch (error) {
    showStatus(progressStatus, error.message, true);
  }
});

refreshButton.addEventListener("click", async () => {
  try {
    const courses = await request("/api/courses");
    renderCourses(courses);
  } catch (error) {
    courseList.textContent = "加载失败，请检查后端服务";
  }
});

request("/api/courses")
  .then(renderCourses)
  .catch(() => {
    courseList.textContent = "加载失败，请检查后端服务";
  });
