import random
import time


# ------------------ EDGE DEVICE (YOLO Simulation) ------------------
class EdgeDevice:
    def __init__(self, id):
        self.id = id
        self.model_version = 1
        self.detection_accuracy = round(random.uniform(0.70, 0.90), 2)  # initial accuracy
        self.data_collected = 0  # simulated number of new frames

    def run_detection(self):
        """Simulate real-time detection on video feed"""
        # Simulate accuracy fluctuation over time
        noise = random.uniform(-0.02, 0.02)
        self.detection_accuracy = max(0.50, min(0.99, self.detection_accuracy + noise))
        detected = random.choice(["Ambulance", "Normal Vehicle", "Fire Truck", "None"])
        confidence = round(random.uniform(0.6, 0.95), 2)
        self.data_collected += random.randint(5, 15)
        print(f"[Edge {self.id}] Detected: {detected} (conf: {confidence}), "
              f"Accuracy: {self.detection_accuracy:.2f}")
        return detected, confidence

    def send_data_to_cloud(self):
        """Send newly collected data for retraining"""
        data_packet = {"edge_id": self.id, "frames": self.data_collected}
        self.data_collected = 0
        return data_packet

    def receive_new_model(self, new_accuracy, new_version):
        """Receive retrained model via CI pipeline"""
        self.model_version = new_version
        self.detection_accuracy = new_accuracy
        print(f"[Edge {self.id}] Model updated to v{new_version}, "
              f"New Accuracy: {new_accuracy:.2f}")


# ------------------ CLOUD CONTROLLER (CI SIMULATION) ------------------
class CloudController:
    def __init__(self):
        self.version_counter = 1
        self.global_accuracy = 0.85
        self.history = []

    def aggregate_data(self, packets):
        total_frames = sum(p["frames"] for p in packets)
        print(f"\n[Cloud CI] Received {total_frames} new frames for retraining.")
        return total_frames

    def retrain_model(self, data_count):
        """Simulate retraining process based on data volume"""
        improvement = min(0.05, data_count / 1000)  # higher data = better improvement
        new_acc = round(min(0.99, self.global_accuracy + improvement), 2)
        self.version_counter += 1
        self.global_accuracy = new_acc
        print(f"[Cloud CI] Retraining complete → New Model v{self.version_counter} "
              f"(Accuracy: {new_acc:.2f})")
        return new_acc, self.version_counter

    def deploy_model(self, edges, acc, version):
        """Push new model to all edge devices"""
        for e in edges:
            e.receive_new_model(acc, version)


# ------------------ SIMULATION LOOP ------------------
if __name__ == "__main__":
    print("Starting Edge Layer YOLO-CI Simulation...\n")

    # Create 3 simulated edge devices (intersections)
    edges = [EdgeDevice(i) for i in range(1, 4)]
    cloud = CloudController()

    for cycle in range(1, 6):  # simulate 5 CI cycles
        print(f"\n CI Cycle {cycle} -----------------------------")

        # Edge devices run detection
        for edge in edges:
            for _ in range(3):  # simulate a few frames per cycle
                edge.run_detection()

        # Send data to cloud for retraining
        data_packets = [e.send_data_to_cloud() for e in edges]
        total_data = cloud.aggregate_data(data_packets)

        # Cloud CI retrains and deploys new model
        new_acc, new_ver = cloud.retrain_model(total_data)
        cloud.deploy_model(edges, new_acc, new_ver)

        time.sleep(1)

    print("\nCI(YOLO) Simulation complete.")
