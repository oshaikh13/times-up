import sys
import time
from pdf2image import convert_from_path
from PIL import Image
import pygame
import os

def pil_to_pygame(image):
    mode = image.mode
    size = image.size
    data = image.tobytes()

    if mode == 'RGBA':
        return pygame.image.fromstring(data, size, 'RGBA').convert_alpha()
    elif mode == 'RGB':
        return pygame.image.fromstring(data, size, 'RGB').convert()
    else:
        image = image.convert('RGB')
        data = image.tobytes()
        return pygame.image.fromstring(data, image.size, 'RGB').convert()

def main():
    if len(sys.argv) != 5:
        print("Usage: python slideshow.py filename.pdf X Y Z")
        sys.exit(1)

    pdf_file = sys.argv[1]
    slide_duration = float(sys.argv[2])
    y_time = float(sys.argv[3])
    z_time = float(sys.argv[4])

    if not (0 < z_time < y_time < slide_duration):
        print("Ensure that 0 < Z < Y < X")
        sys.exit(1)

    # Convert PDF to images
    pages = convert_from_path(pdf_file)

    # Initialize Pygame
    pygame.init()
    initial_width, initial_height = 800, 600  # Set initial window size
    screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
    pygame.display.set_caption('Slideshow')
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()

    # Load slides
    slides_original = []
    for page in pages:
        image = pil_to_pygame(page)
        slides_original.append(image)

    # Prepare resized slides
    def resize_slides():
        screen_width, screen_height = screen.get_size()
        resized_slides = []
        for image in slides_original:
            # Calculate scaling factor to maintain aspect ratio
            page_width, page_height = image.get_size()
            page_ratio = page_width / page_height
            screen_ratio = screen_width / screen_height

            if page_ratio > screen_ratio:
                # Fit to screen width
                new_width = screen_width
                new_height = int(screen_width / page_ratio)
            else:
                # Fit to screen height
                new_height = screen_height
                new_width = int(screen_height * page_ratio)

            resized_image = pygame.transform.smoothscale(image, (new_width, new_height))
            image_rect = resized_image.get_rect(center=(screen_width / 2, screen_height / 2))
            resized_slides.append((resized_image, image_rect))
        return resized_slides

    slides = resize_slides()

    running = True
    current_slide = 0
    slide_start_time = time.time()
    time_remaining = slide_duration

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                    # Next slide
                    current_slide = (current_slide + 1) % len(slides)
                    slide_start_time = time.time()
                    time_remaining = slide_duration
                elif event.key == pygame.K_LEFT:
                    # Previous slide
                    current_slide = (current_slide - 1) % len(slides)
                    slide_start_time = time.time()
                    time_remaining = slide_duration
                elif event.key == pygame.K_r:
                    # Reset timer
                    slide_start_time = time.time()
                    time_remaining = slide_duration
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                slides = resize_slides()
                screen_width, screen_height = screen.get_size()

        # Update time_remaining
        time_elapsed = time.time() - slide_start_time
        time_remaining = slide_duration - time_elapsed

        if time_remaining <= 0:
            # Move to next slide
            current_slide = (current_slide + 1) % len(slides)
            slide_start_time = time.time()
            time_remaining = slide_duration

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the slide
        image, image_rect = slides[current_slide]
        screen.blit(image, image_rect)

        # Prepare countdown text
        countdown_text = int(time_remaining) + 1  # +1 to show countdown

        if time_remaining > y_time:
            # Default small black font in top-right corner
            font_size = int(screen_height / 15)
            font_color = (0, 0, 0)
            position = (screen_width - 10, 10)  # Top-right corner
            anchor = 'topright'
        elif y_time >= time_remaining > z_time:
            # Bigger red font in top-right corner
            font_size = int(screen_height / 6)
            font_color = (255, 0, 0)
            position = (screen_width - 10, 10)  # Top-right corner
            anchor = 'topright'
        else:
            # Even bigger red font in center
            font_size = int(screen_height / 3)
            font_color = (255, 0, 0)
            position = (screen_width / 2, screen_height / 2 - font_size / 2)  # Center
            anchor = 'center'

        # Render countdown text
        font = pygame.font.SysFont('Arial', font_size, bold=True)

        # format the countdown text as minutes:seconds
        if time_remaining > 60:
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            countdown_text = f"{minutes}:{seconds:02d}"
        else:
            countdown_text = f"{int(time_remaining)}"

        text_surface = font.render(countdown_text, True, font_color)
        text_rect = text_surface.get_rect()
        setattr(text_rect, anchor, position)

        if time_remaining <= z_time:
            font_timesup = pygame.font.SysFont('Arial', font_size // 4, bold=True)  # Smaller font
            timesup_text_surface = font_timesup.render("TIME FOR YOUR LAST WORDS", True, (255, 0, 0))
            timesup_text_rect = timesup_text_surface.get_rect(center=(screen_width / 2, screen_height / 2 + font_size / 2))
            screen.blit(timesup_text_surface, timesup_text_rect)

        # Draw white background rectangle behind text
        padding = 10  # Adjust padding as needed
        background_rect = text_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(screen, (255, 255, 255), background_rect)
        # Blit text onto screen
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        pygame.quit()
        raise e
