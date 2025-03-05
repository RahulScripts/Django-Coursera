from django.shortcuts import render, redirect
from .forms import BookingForm

def booking_view(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the data to the database
            return redirect('booking')  # Redirect to avoid form resubmission
    else:
        form = BookingForm()
    
    return render(request, 'myapp/booking.html', {'form': form})
