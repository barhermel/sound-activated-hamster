import io
from google.cloud import speech
import sounddevice as sd
import os
import rospy
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/bar/hamster-sound-activated/google.json"

def get_drive_msg(angle_deg, speed): #function to make the drive more easy
	ack_msg = AckermannDriveStamped()
	ack_msg.header.stamp = rospy.Time.now()
	ack_msg.header.frame_id = ''
	ack_msg.drive.steering_angle = angle_deg * 0.0174532925;
	ack_msg.drive.speed = speed;
	return ack_msg;

def record():
    print("started recording...")
    duration = 2  # seconds
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True, dtype='int16')
    print("finished recording, recognizing audio")

    client = speech.SpeechClient()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='he-IL', sample_rate_hertz=44100)
    audio = speech.types.RecognitionAudio(content=recording.tobytes())
    results = client.recognize(config=config, audio=audio)

    for result in results.results:
        for alternative in result.alternatives:
            print('=' * 20)
            print('transcript: ' + alternative.transcript)
            print('confidence: ' + str(alternative.confidence))
            return alternative.transcript


if __name__ == '__main__':
	rospy.init_node('voice-activated', anonymous=True)
	ackermann = rospy.Publisher('/agent1/ackermann_cmd', AckermannDriveStamped, queue_size=1)

	while True:
		print("press enter to record voice command")
		input()
		text = record()
		if text is None:
			print("did not recognize command");
			continue;
		if "ישר" in text:
			ackermann.publish(get_drive_msg(0, 1))
			continue;
		if "לה" in text or "שמאל" in text:
			ackermann.publish(get_drive_msg(-90, 1))
			continue;
		if "מי" in text:
			ackermann.publish(get_drive_msg(90, 1))
			continue;
		if "רה" in text or "רס" in text:
			ackermann.publish(get_drive_msg(0, -1))
			continue;
