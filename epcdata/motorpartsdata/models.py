from django.db import models

# Serial number, always unique
class SerialNumber(models.Model):
    serial = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.serial

# Parent title, linked to SerialNumber
class ParentTitle(models.Model):
    title = models.CharField(max_length=200)
    serial_number = models.ForeignKey(SerialNumber, on_delete=models.CASCADE, related_name='parent_titles')

    def __str__(self):
        return self.title

# Child title, linked to ParentTitle, with its own SVG code
class ChildTitle(models.Model):
    title = models.CharField(max_length=200)
    parent = models.ForeignKey(ParentTitle, on_delete=models.CASCADE, related_name='child_titles')
    svg_code = models.TextField()

    def __str__(self):
        return self.title

# Part details, linked to ChildTitle (which indirectly gives us SVG and parent info)
class Part(models.Model):
    child_title = models.ForeignKey(ChildTitle, on_delete=models.CASCADE, related_name='parts')
    
    call_out_order = models.IntegerField()
    part_number = models.CharField(max_length=100)
    usage_name = models.CharField(max_length=200)
    unit_qty = models.CharField(max_length=100)
    lr = models.CharField(max_length=10, blank=True, null=True)  # Left/Right
    remark = models.TextField(blank=True, null=True)
    nn_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.part_number} - {self.usage_name}"
