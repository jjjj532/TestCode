use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::Duration;

use tauri::Manager;

struct BackendState {
    child: Option<Child>,
    port: u16,
}

impl BackendState {
    fn new(port: u16) -> Self {
        Self { child: None, port }
    }

    fn kill_port(&self, port: u16) -> Result<(), String> {
        #[cfg(target_os = "macos")]
        {
            let output = Command::new("lsof")
                .args(["-ti", &format!(":{}", port)])
                .output()
                .map_err(|e| format!("Failed to check port: {e}"))?;
            
            let pids = String::from_utf8_lossy(&output.stdout);
            for pid in pids.lines() {
                if let Ok(pid) = pid.trim().parse::<u32>() {
                    Command::new("kill")
                        .args(["-9", &pid.to_string()])
                        .output()
                        .map_err(|e| format!("Failed to kill process: {e}"))?;
                }
            }
        }
        Ok(())
    }

    fn start(&mut self) -> Result<(), String> {
        // Kill any existing process on the port
        self.kill_port(self.port)?;
        
        // Wait for port to be released
        std::thread::sleep(Duration::from_millis(500));
        
        // Try to find the TestCode project root
        let possible_paths: Vec<PathBuf> = vec![
            PathBuf::from("/Users/mac/AI/TestCode"),
            PathBuf::from("."),
        ];
        
        let project_root = possible_paths
            .iter()
            .find(|p| p.join("packages/server/src/testcode_server/app.py").exists())
            .cloned()
            .ok_or("Could not find TestCode project root")?;
        
        let server_path = project_root.join("packages/server");
        let python_path = server_path.to_string_lossy().to_string();
        
        eprintln!("Project root: {}", project_root.display());
        eprintln!("Server path: {}", python_path);

        // Start the TestCode server
        let mut cmd = Command::new("python3");
        cmd.env("PYTHONPATH", &python_path);
        cmd.current_dir(&project_root);
        cmd.args([
            "-m",
            "testcode_server.app",
            "--port",
            &self.port.to_string(),
            "--host",
            "127.0.0.1",
        ]);

        let child = cmd
            .stdout(Stdio::inherit())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|e| format!("Failed to start backend: {e}"))?;

        self.child = Some(child);
        Ok(())
    }

    fn stop(&mut self) {
        if let Some(ref mut child) = self.child {
            let _ = child.kill();
            let _ = child.wait();
            self.child = None;
        }
    }
}

async fn wait_for_health(port: u16) -> Result<(), String> {
    let url = format!("http://127.0.0.1:{}/health", port);
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {e}"))?;

    for _ in 0..50 {
        match client.get(&url).send().await {
            Ok(resp) if resp.status().is_success() => return Ok(()),
            _ => tokio::time::sleep(Duration::from_millis(200)).await,
        }
    }
    Err(format!("Backend at {url} did not become ready within 10 seconds"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port: u16 = 8000;
    let mut backend = BackendState::new(port);

    tauri::Builder::default()
        .setup(move |app| {
            // Start backend
            if let Err(e) = backend.start() {
                eprintln!("{e}");
            }

            let window = app.get_webview_window("main").ok_or("no main window")?;

            tauri::async_runtime::spawn(async move {
                match wait_for_health(port).await {
                    Ok(()) => {
                        let url = url::Url::parse(&format!("http://127.0.0.1:{}?desktop=true", port))
                            .expect("invalid URL");
                        let _ = window.navigate(url);
                    }
                    Err(e) => {
                        eprintln!("{e}");
                    }
                }
            });

            app.manage(Mutex::new(backend));

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Some(state) = window.try_state::<Mutex<BackendState>>() {
                    if let Ok(mut backend) = state.lock() {
                        backend.stop();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}
