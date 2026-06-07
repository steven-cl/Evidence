from OpenGL.GL import * # pyright: ignore[reportMissingImports]
from OpenGL.GLU import * # pyright: ignore[reportMissingImports]
import pygame # pyright: ignore[reportMissingImports]
import math

class CameraFPS:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Detective's position in the world (X, Y, Z)
        self.pos_x = 0.0
        self.pos_y = 1.5  # Initial viewing height
        self.pos_z = 5.0
        
        # Rotation of the head (in degrees)
        self.pitch = 0.0   # Up / Down
        self.yaw = -90.0   # Left / Right (Starts looking at the center)

        # Direction vectors of the camera
        self.front_x = 0.0
        self.front_y = 0.0
        self.front_z = -1.0

        self.right_x = 1.0
        self.right_z = 0.0

        # Adjustable control parameters
        self.speed = 4.0        # Detective's walking speed
        self.sensitivity = 0.1  # Mouse sensitivity

        # Update the initial viewing vectors
        self.update_camera_vectors()

    def configure_projection(self):
        """
        Configures the camera's perspective. Called at startup.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def update_camera_vectors(self):
        """
        Calculates mathematically where the camera is looking based on Yaw and Pitch.
        """
        # Convert angles to radians for trigonometric functions in Python
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # Calculate the new Front vector (Looking Forward)
        self.front_x = math.cos(yaw_rad) * math.cos(pitch_rad)
        self.front_y = math.sin(pitch_rad)
        self.front_z = math.sin(yaw_rad) * math.cos(pitch_rad)

        # Normalize the Front vector to maintain constant speed
        length = math.sqrt(self.front_x**2 + self.front_y**2 + self.front_z**2)
        self.front_x /= length
        self.front_y /= length
        self.front_z /= length

        # Calculate the Right vector (Right side of the camera) using the Cross Product (without altering the Y axis)
        # This prevents the detective from floating or sinking when moving forward while looking up/down
        r_length = math.sqrt(self.front_z**2 + (-self.front_x)**2)
        self.right_x = self.front_z / r_length
        self.right_z = -self.front_x / r_length

    def process_mouse(self, dx, dy):
        """
        Processes relative mouse input data received from the application 
        event loop to update camera yaw and pitch orientations.
        """
        # Apply orientation updates scaled by internal movement sensitivity factor
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity  # Inverted for standard FPS look behavior

        # Clamp vertical viewing pitch dynamics to prevent full camera inversion inversion
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Synchronize and recalculate direct mathematical target orientation vectors
        self.update_camera_vectors()

    def process_keyboard(self, dt):
        """
        Moves the detective's position based on the keys pressed.
        dt: Delta Time (time elapsed per frame) to ensure homogeneous movement.
        """
        keys = pygame.key.get_pressed()
        velocity = self.speed * dt

        # Movement forward / backward in the horizontal plane (X, Z)
        if keys[pygame.K_w]:
            self.pos_x += self.front_x * velocity
            self.pos_z += self.front_z * velocity
        if keys[pygame.K_s]:
            self.pos_x -= self.front_x * velocity
            self.pos_z -= self.front_z * velocity

        # Sideways movement (Strafe) Left / Right
        if keys[pygame.K_a]:
            self.pos_x += self.right_x * velocity
            self.pos_z += self.right_z * velocity
        if keys[pygame.K_d]:
            self.pos_x -= self.right_x * velocity
            self.pos_z -= self.right_z * velocity

    def update_view(self):
        """
        Applies the final transformations to OpenGL using the LookAt matrix.
        Called in each iteration of the main game loop.
        """
        glLoadIdentity()
        
        # Point in 3D space where the detective is looking
        target_x = self.pos_x + self.front_x
        target_y = self.pos_y + self.front_y
        target_z = self.pos_z + self.front_z

        # Define the camera: Current position, Look-at point, Up vector (Y=1)
        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )